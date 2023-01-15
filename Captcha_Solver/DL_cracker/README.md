If you are NOT using ephemeral instance like Google Colab or Kaggle notebook, it is highly recommended that you create a
[virtual environment](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html) before installing the packages.

First, install `mmcv` by following [this instruction](https://mmcv.readthedocs.io/en/latest/get_started/installation.html)
or running this command
```
pip install mmcv-full
```

Next, go to the `captcha` folder and run
```
pip install -e .
```

Similarly, go to the `mmdetection` folder and run
```
pip install -e .
```