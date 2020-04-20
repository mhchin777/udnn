from _udnn import Model as _Model, TensorBase
import numpy as np
import tensorflow as tf
from .tensor import tensor


class Model:
    def __init__(self):
        self.__model = _Model()
        # book keeping here as well
        self.__layers = []

    def add_layer(self, layer_name, layer):
        self.__model.add_layer(layer_name, layer)
        self.__layers.append(layer)

    def predict(self, input_tensor):
        out_type = self.__model.out_type()
        if not isinstance(input_tensor, TensorBase):
            input_tensor = tensor(input_tensor, out_type)
        self.__model.predict(input_tensor)
        if out_type == "Int8":
            return self.__model.out_as_Int8()
        elif out_type == "Int16":
            return self.__model.out_as_Int16()
        elif out_type == "Int32":
            return self.__model.out_as_Int32()
        elif out_type == "Int64":
            return self.__model.out_as_Int64()
        elif out_type == "Float":
            return self.__model.out_as_Float()
        elif out_type == "Double":
            return self.__model.out_as_Double()

    def get_layer(self, index):
        return self.__layers[index]

    @staticmethod
    def __get_weights(weights, w_i):
        w_ = weights[w_i]
        if isinstance(w_, tf.Variable):
            w_ = w_.numpy()
        return w_

    def load_weights(self, weights):
        w_i = 0
        for i in range(len(self.__layers)):
            layer = self.__layers[i]
            if layer.has_weights:
                w = np.reshape(self.__get_weights(weights, w_i),
                               layer.weights_size.tuple())
                w_i += 1
                layer.load_weights(w)
            if layer.has_bias:
                b = np.reshape(self.__get_weights(weights, w_i),
                               layer.bias_size.tuple())
                layer.load_bias(b)
                w_i += 1
        if w_i != len(weights):
            raise ValueError("Weights size doesn't match")

    def dump_weights_to_dir(self, dir_name):
        import os
        for layer in self.__layers:
            if layer.has_weights:
                # suffix _w for weights
                name = layer.name + "_w.data"
                filename = os.path.join(dir_name, name)
                layer.weights.dump(filename)
            if layer.has_bias:
                # suffix _b for bias
                name = layer.name + "_b.data"
                filename = os.path.join(dir_name, name)
                layer.bias.dump(filename)

    def load_weights_from_dir(self, dir_name):
        import os
        for layer in self.__layers:
            if layer.has_weights:
                # suffix _w for weights
                name = layer.name + "_w.data"
                filename = os.path.join(dir_name, name)
                layer.weights.load(filename)
            if layer.has_bias:
                # suffix _b for bias
                name = layer.name + "_b.data"
                filename = os.path.join(dir_name, name)
                layer.bias.load(filename)
