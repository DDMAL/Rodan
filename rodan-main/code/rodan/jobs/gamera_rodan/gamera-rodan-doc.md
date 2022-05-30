# Documentation of installing and running Gamera4 on Rodan

## *Here you can find the documentation for running Gamera4 on the Python3Celery Rodan container*

**NOTE: Py3 container's docker file will have the instructions built-in. This doc is to only assist you with the understanding of how Gamera4 is run on the container.**

---

## To install Gamera-4 do the following:

* Inside the container, run `cd /`.
* Run `apt upgrade` and after updating apt, run `apt-get install libpng-dev &&  apt-get install libtiff5-dev` to install the dependencies for some of Gamera4 C++ files.
* Run `git clone https://github.com/hsnr-gamera/gamera-4.git` to have Gamera4 downloaded in the root directory of the container.

* `cd gamera-4` and run the following command: `python3.7 setup.py --nowx build && python3.7 setup.py --nowx install`.
  * If the process is terminated with an error such as below:
  <br>

    ```python
    internal_png_dir not found 
    ```
    You have to __```vim```__ to the python file throwing the error. Then replace ```os.path.join(internal_png_dir, x) for x in``` with ```("src/libpng-1.2.5/" + x) for x in``` (in the line that the error comes from) and retry.

* You have successfully built and installed Gamera4 on the container. Now, you can remove **gamera-4** directory by running `cd && cd .. && rm -rf gamera-4`

* To test if Gamera4 is working properly or not, you can create a python test script and use Gamera4's methods. For instance: <br>

    ```python
    from gamera.core import *
    from gamera.plugins.png_support import load_PNG

    def test(image):
        img = load_image(image)
        img2 = img.to_onebit()
        img2.save_PNG("out.png")

    if __name__ == "__main__":
        image = "in.png"
        init_gamera()
        test(image)
    ```
Author: Shahrad Mohammadzadeh

---