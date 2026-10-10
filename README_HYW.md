# 训练数据集 以及 训练方法

本页保留早期调研问题及参考链接。服务化 API 已实现，当前部署、数据集/任务接口、训练验证分别见 [SERVICE_DEPLOYMENT.md](SERVICE_DEPLOYMENT.md)、[LORA_TRAINING_API.md](LORA_TRAINING_API.md) 和 [SERVICE_TEST_REPORT.md](SERVICE_TEST_REPORT.md)。Flux2 Klein 9B 20 步短训已通过，不等于全部调研问题、模型质量或长期训练已经验收；系统部署不得依照参考链接另下载模型。

https://blog.csdn.net/weixin_29069575/article/details/160539184


https://www.liblib.art/pretrain

https://rickypro.cn/2026/05/12/FLUX2-Klein-9B-%E6%90%AD%E5%BB%BA%E6%96%B9%E6%A1%88/

https://github.com/cocktailpeanut/fluxgym

# 需要弄清楚的问题
1. 训练数据集如何构建
2. 训练参数：模拟9b-fp8 如何训练对应尺寸的lora
3. lora 如何加载
4. 本项目是否可以部署成服务，然后调用api进行训练呢
