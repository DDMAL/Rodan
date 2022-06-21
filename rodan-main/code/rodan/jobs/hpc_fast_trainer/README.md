# HPC Fast Trainer

This is a version of the [Patchwise trainer job in Rodan](https://github.com/DDMAL/Calvo-classifier) that, instead of
running on a local machine, is sent to a HPC cluster. RabbitMQ is used to pass messages between this and the
[corresponding job that runs on the cluster](https://github.com/JRegimbal/hpc-trainer-component).
