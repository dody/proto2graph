# proto2graph

Generate [GraphViz] files from [Google Protocol Buffer] definitions. 

## Example results:

- [gNOI CertificateManagement](cert_pb2.dot.svg)
- [gNMI](gnmi_070_pb2.dot.svg)

## Requirements

- python2
- install `protobuf` into python using `pip`

        pip install protobuf

## How to

1) Compile your proto files. If you dont know how, here is tutorial: https://developers.google.com/protocol-buffers/docs/pythontutorial

2) Feed python files to `proto2graph.py` to generate graphviz `.dot` files

        python proto2graph.py cert_pb2.py

3) Visualize `.dot` files using offline tools or use simple web app <https://dreampuf.github.io/GraphvizOnline>

## Help

~~~
Usage: proto2graph.py [options] <compiled proto files *.py>

Options:
  -h, --help            show this help message and exit
  -r ORIENTATION, --orientation=ORIENTATION
                        Orientation of graph: TD = Top -> Down, LR = Left ->
                        Right [default: LR]
  -f FONT_TYPE, --font=FONT_TYPE
                        Font type [default: Bitstream Vera Sans]
  --font-size=FONT_SIZE
                        Font size [default: 9]
  -x EXCLUDE, --exclude=EXCLUDE
                        Exclude field/message names matching the specified
                        regexp pattern
  -d, --debug           Print debug info [default: False]
  -o OUTPUT, --output=OUTPUT
                        Output directory [default: .]
~~~

## Credits

Project is based on <https://github.com/lazics/proto2dot>
I did NOT make a fork becasue I have removed features from original project such as compiling proto file and compiling dot file into image. Code is smaller and it was easier to catch bugs.

[GraphViz]: http://www.graphviz.org/
[Google Protocol Buffer]: https://code.google.com/p/protobuf/
