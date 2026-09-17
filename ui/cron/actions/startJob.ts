import prisma from '../prisma';
import { spawn } from 'child_process';
import path from 'path';
import fs from 'fs';
import { TOOLKIT_ROOT, getTrainingFolder, getHFToken } from '../paths';
import { resolvePythonPath } from '../pythonPath';

export default async function startJob(jobID: string) {
  const job = await prisma.job.findUnique({ where: { id: jobID } });
  if (!job) return;
  const claim = await prisma.job.updateMany({
    where: { id: jobID, status: 'queued', stop: false },
    data: { status: 'running', info: 'Starting job...', pid: null },
  });
  if (!claim.count) return;
  const fail = async (info: string) => {
    await prisma.job.updateMany({
      where: { id: jobID, status: { in: ['running', 'stopping'] } },
      data: { status: 'error', info, pid: null },
    });
  };
  let logFd: number | undefined;
  try {
    const trainingRoot = await getTrainingFolder();
    const folder = path.join(trainingRoot, job.name);
    fs.mkdirSync(folder, { recursive: true });
    const configPath = path.join(folder, '.job_config.json');
    const logPath = path.join(folder, 'log.txt');
    if (fs.existsSync(logPath)) {
      const logs = path.join(folder, 'logs');
      fs.mkdirSync(logs, { recursive: true });
      let n = 0;
      while (fs.existsSync(path.join(logs, `${n}_log.txt`))) n++;
      fs.renameSync(logPath, path.join(logs, `${n}_log.txt`));
    }
    const config = JSON.parse(job.job_config);
    config.config.process[0].sqlite_db_path = path.join(TOOLKIT_ROOT, 'aitk_db.db');
    config.config.process[0].training_folder = trainingRoot;
    config.config.name = job.name;
    fs.writeFileSync(configPath, JSON.stringify(config, null, 2));
    const python = resolvePythonPath();
    const hfToken = await getHFToken();
    // Capture failures before Python's own logging has initialized.
    logFd = fs.openSync(logPath, 'a');
    const child = spawn(python, ['-u', path.join(TOOLKIT_ROOT, 'run.py'), configPath], {
      cwd: TOOLKIT_ROOT, detached: true, windowsHide: true,
      stdio: ['ignore', logFd, logFd],
      env: {
        ...process.env, AITK_JOB_ID: jobID, CUDA_DEVICE_ORDER: 'PCI_BUS_ID',
        CUDA_VISIBLE_DEVICES: job.gpu_ids, IS_AI_TOOLKIT_UI: '1',
        ...(hfToken ? { HF_TOKEN: hfToken } : {}),
      },
    });
    // Install listeners before awaiting DB updates; preserve trainer terminal states.
    child.once('error', error => void fail(`Python launch failed: ${error.message}`).catch(console.error));
    child.once('exit', (code, signal) => {
      void fail(`Python exited before completion (code=${code}, signal=${signal})`).catch(console.error);
    });
    if (child.pid) {
      await prisma.job.updateMany({ where: { id: jobID, status: 'running' }, data: { pid: child.pid } });
      fs.writeFileSync(path.join(folder, 'pid.txt'), String(child.pid));
    }
    child.unref();
  } catch (error) {
    await fail(`Error launching job: ${error instanceof Error ? error.message : String(error)}`);
  } finally {
    if (logFd !== undefined) fs.closeSync(logFd);
  }
}
