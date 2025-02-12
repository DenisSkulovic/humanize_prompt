1) Fix the await in the worker script, which makes the worker await all the chunks first, then stream them into the RabbitMQ for the API to consume.

2) Change the way the worker interacts with RabbitMQ, because currently, if I were to use several worker instances, they would all consume all task messages. Instead they should race for tasks and acknowledge them as soon as they are done.

3) Add an nginx service into docker-compose.yml, which will be used to reverse proxy the API.

All of these changes would allow for a real scalable setup. I could use, say, 3 api instance and 10 worker instances.

Additional: Fix the issue of lanching the API instance for the first time when the database is not initalized. It fails, and works when started the second time and later. Only the first launch with an empty DB fails.