import { NextRequest, NextResponse } from 'next/server';
import { PrismaClient } from '@prisma/client';
import { execFile } from 'child_process';
import { promisify } from 'util';

const execFileAsync = promisify(execFile);
const prisma = new PrismaClient();

export async function GET(request: NextRequest, { params }: { params: { jobID: string } }) {
  const { jobID } = await params;
  const cancelled = await prisma.job.updateMany({
    where: { id: jobID, status: 'queued' },
    data: { stop: true, status: 'stopped', return_to_queue: false, info: 'Job stopped', pid: null },
  });
  const job = await prisma.job.findUnique({ where: { id: jobID } });
  if (!job) return NextResponse.json({ error: 'Job not found' }, { status: 404 });
  if (cancelled.count || !['running', 'stopping'].includes(job.status)) {
    return NextResponse.json(job);
  }
  // Keep the GPU queue occupied until the process actually exits.
  await prisma.job.updateMany({
    where: { id: jobID, status: { in: ['running', 'stopping'] } },
    data: { stop: true, status: 'stopping', info: 'Stopping job...' },
  });
  if (job.pid != null) {
    try {
      if (process.platform === 'win32') {
        await execFileAsync('taskkill', ['/PID', String(job.pid), '/T', '/F'], { windowsHide: true });
      } else {
        process.kill(job.pid, 'SIGINT');
      }
    } catch (error: any) {
      if (error.code === 'ESRCH') {
        await prisma.job.updateMany({
          where: { id: jobID, status: 'stopping', pid: job.pid },
          data: { status: 'stopped', info: 'Process already exited', pid: null },
        });
      } else {
        return NextResponse.json({ error: 'Failed to signal training process' }, { status: 500 });
      }
    }
  }
  return NextResponse.json(await prisma.job.findUnique({ where: { id: jobID } }));
}
