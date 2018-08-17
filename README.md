# EPypes 

EPypes (for *event-driven piplines*) is a Python library for developing data processing algorithms in a form of computational graphs and their integration with distributed systems based on publish-subscribe communication. The initial use case of EPypes is computer vision alogorithms development, although it is suitable for any algorithm that can be expressed as a directed acyclic graph. 

EPypes facilitates flexibility of algorithm prototyping, as well as provides a structured approach to managing algorithm logic and exposing the developed pipelines as a part of on-line publish-subscribe systems. Currently, ZeroMQ middleware is supported, with data serialization based on Protocol Buffers.

## Modules

The most important modules include:

 * `compgraph`, `graph` -- primitives for construction and execution of computational graphs
 * `pipeline`, `node` -- primitives for extendind computational graphs with additional functionality, specifically the reactive behavior
 * `zeromq` -- adapters to ZeroMQ middleware
 * `reactivevision` -- functionality for creation of reactive computer vision components

## Installation and requirements

The core dependencies for the EPypes codebase include `pyzmq`, `protobuf`, and `networkx>=2.0`. They are listed in the `requirements.txt` file, and can be installed in one of the following ways:

```bash
# using pip
$ pip install -r requirements.txt

# using conda
$ while read requirement; do conda install --yes $requirement -c conda-forge; done < requirements.txt
```

## Usage examples

The example below demostrates construction and execution of a computational graph. The demonstrated algorithm accepts a BGR image, converts it to grayscale, blurs the grayscale, and feeds the blurred image to the Canny edge detector.

```python
import cv2
from epypes.compgraph import CompGraph
from epypes.compgraph import CompGraphRunner

def grayscale(im):
    return cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)

def gaussian_blur(im, kernel_size):
    return cv2.GaussianBlur(im, (kernel_size, kernel_size), 0)

if __name__ == '__main__':

    func_dict = {
        'grayscale': grayscale,
        'canny': cv2.Canny,
        'blur': gaussian_blur
    }

    func_io = {
        'grayscale': ('image', 'image_gray'),
        'blur': (('image_gray', 'blur_kernel'), 'image_blurred'),
        'canny': (('image_blurred', 'canny_lo', 'canny_hi'), 'edges'),
    }

    hparams = {
        'blur_kernel': 11,
        'canny_lo': 70,
        'canny_hi': 200
    }

    cg = CompGraph(func_dict, func_io)
    runner = CompGraphRunner(cg, hparams)

    im = cv2.imread('my_image.jpg', cv2.IMREAD_COLOR)
    runner.run(image=im)
```

For more complex computational graphs examples, refer to the following Jupyter notebooks:

 * [Simple lane lines detection (Udacity CarND project)](https://github.com/semeniuta/CarND-LaneLines-P1/blob/master/P1_1_Pipeline_demo.ipynb)
 * [More advanced lane lines detection (Udacity CarND project)](https://github.com/semeniuta/CarND-Advanced-Lane-Lines/blob/master/7_pipeline_prototyping_3.ipynb)
