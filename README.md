# TFX Sandbox

TFX is an amazing tool for production, as many Google products can testify. But it can also be used before production, during the development phase, in order to reduce the time needed between dev and prod. Let's see in this tutorials how one can leverage this tool in order to improve the development experience.

## How to run the tutorial
```
docker build -t tfx-sandbox .
docker run -p 8081:8081 -p 8080:8080 -p 6006:6006 tfx-sandbox
```

* Copy the jupyter token from the shell (from a line like this `http://(964b032d2326 or 127.0.0.1):8081/?token=1453e4b7fb1014133430915443f2c7e5f1c9b88205f3f0d5`)
)
* Open [Tutorial](http://localhost:8081/notebooks/tutorials/titanic/tfx-tutorial.ipynb) and past the token.