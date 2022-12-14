# Copyright 2022 The KerasNLP Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Tests for XLM-RoBERTa task specific models and heads."""

import os

import tensorflow as tf
from absl.testing import parameterized
from tensorflow import keras

from keras_nlp.models.xlm_roberta.xlm_roberta_backbone import XLMRobertaBackbone
from keras_nlp.models.xlm_roberta.xlm_roberta_classifier import (
    XLMRobertaClassifier,
)


class XLMRobertaClassifierTest(tf.test.TestCase, parameterized.TestCase):
    def setUp(self):
        self.model = XLMRobertaBackbone(
            vocabulary_size=1000,
            num_layers=2,
            num_heads=2,
            hidden_dim=64,
            intermediate_dim=128,
            max_sequence_length=128,
        )
        self.batch_size = 8
        self.input_batch = {
            "token_ids": tf.ones(
                (self.batch_size, self.model.max_sequence_length), dtype="int32"
            ),
            "padding_mask": tf.ones(
                (self.batch_size, self.model.max_sequence_length), dtype="int32"
            ),
        }

        self.input_dataset = tf.data.Dataset.from_tensor_slices(
            self.input_batch
        ).batch(2)

    def test_valid_call_classifier(self):
        classifier = XLMRobertaClassifier(self.model, 4, 128, name="classifier")
        classifier(self.input_batch)

    @parameterized.named_parameters(
        ("jit_compile_false", False), ("jit_compile_true", True)
    )
    def test_xlm_roberta_classifier_compile(self, jit_compile):
        classifier = XLMRobertaClassifier(self.model, 4, 128, name="classifier")
        classifier.compile(jit_compile=jit_compile)
        classifier.predict(self.input_batch)

    @parameterized.named_parameters(
        ("jit_compile_false", False), ("jit_compile_true", True)
    )
    def test_xlm_roberta_classifier_compile_batched_ds(self, jit_compile):
        classifier = XLMRobertaClassifier(self.model, 4, 128, name="classifier")
        classifier.compile(jit_compile=jit_compile)
        classifier.predict(self.input_dataset)

    @parameterized.named_parameters(
        ("tf_format", "tf", "model"),
        ("keras_format", "keras_v3", "model.keras"),
    )
    def test_saved_model(self, save_format, filename):
        classifier = XLMRobertaClassifier(self.model, 4, 128, name="classifier")
        classifier_output = classifier(self.input_batch)
        save_path = os.path.join(self.get_temp_dir(), filename)
        classifier.save(save_path, save_format=save_format)
        restored_classifier = keras.models.load_model(save_path)

        # Check we got the real object back.
        self.assertIsInstance(restored_classifier, XLMRobertaClassifier)

        # Check that output matches.
        restored_output = restored_classifier(self.input_batch)
        self.assertAllClose(classifier_output, restored_output)