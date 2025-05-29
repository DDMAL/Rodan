# Python3 Celery

This Docker contains the following jobs:
| Job title | Link/Info |
| --------- | ---- |
| `pixel_wrapper` | https://github.com/DDMAL/pixel_wrapper.git |
| `neon_wrapper` | https://github.com/DDMAL/neon_wrapper |
| `gamera` | Pre-built Docker Image [ddmal/gamera4:2.0.0](FROM ddmal/gamera4:2.0.0 AS gamera) |

The container uses `celery` to spin up multiple **workers** that process **jobs**. Each **job** is executed when a **worker** becomes available and a task is present in the RabbitMQ broker queue.