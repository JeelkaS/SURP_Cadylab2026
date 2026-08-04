import tensorflow as tf
from tensorflow import keras
import numpy as np
from sklearn.cluster import KMeans

# attempts to push the weights so that the highest output column value
# is "margin" anount higher than the next highest
# in combination with the sparse catigorical crossentropy loss
# this is to try and make it easier to translate weights to resistance
# (to be honest I'm not sure how much this is doing but I'm leaving it in case
# it's helping or has the potential to help)
def sparse_ce_with_margin(y_true, logits, margin=0.2):
    """
    y_true: training labels
    logits: model outputs
    margin: desired gap between correct logit and others
    """

    # first, do normal sparse categorical cross-entropy
    ce_loss = keras.losses.sparse_categorical_crossentropy(y_true, logits, from_logits=True)

    # get correct class logit and highest incrorect logit
    # get set of one-hot vectors based on labels in batch
    y_true_one_hot = tf.one_hot(tf.cast(y_true, tf.int32), depth=tf.shape(logits)[-1])
    # multiply the one-hots and the raw outputs (no softmax) so incorrect cols go to 0
    # and then add the results from each set of logits together, leaving one value for each
    correct_logit = tf.reduce_sum(y_true_one_hot * logits, axis=-1, keepdims=True)
    # mask correct class so it doesn't see it as the max
    wrong_logits = logits - y_true_one_hot * 1e9
    # find the largest incorrect column value
    max_wrong_logit = tf.reduce_max(wrong_logits, axis=-1, keepdims=True)

    # if less than margin is between correct and highest incorrect, add proportional loss
    margin_penalty = keras.activations.relu(max_wrong_logit - correct_logit + margin)
    return ce_loss + margin_penalty

# determines that it's correct if there's only one maximum and it's
# the correct one, because there was an issue with regular ['accuracy'] metric
# where it would say it was correct even if there was a tie between two columns
@tf.keras.utils.register_keras_serializable()
class strict_accuracy(tf.keras.metrics.Metric):
    def __init__(self, name="strict_accuracy", **kwargs):
        super().__init__(name=name, **kwargs)
        self.total = self.add_weight(name="total", initializer="zeros")
        self.correct = self.add_weight(name="correct", initializer="zeros")

    def update_state(self, y_true, y_pred, sample_weight=None):
        # convert y_true to integer labels if one-hot
        if y_true.shape.rank > 1 and y_true.shape[-1] > 1:
            y_true = tf.argmax(y_true, axis=-1)

        # finx max probability for each sample
        max_vals = tf.reduce_max(y_pred, axis=-1, keepdims=True)
        # Boolean mask to find indices equal to the max
        ties = tf.cast(tf.equal(y_pred, max_vals), tf.int32)
        # count the ties in each row
        num_ties = tf.reduce_sum(ties, axis=-1)
        # if there's only 1 max, count this part of the accuracy as correct
        unique_max = tf.equal(num_ties, 1)
        unique_max_f = tf.cast(unique_max, tf.float32)

        # find which class was predicted
        pred_class = tf.argmax(y_pred, axis=-1)

        # correct only if correct prediction and only 1 max
        correct_prediction = tf.logical_and(
            unique_max,
            tf.equal(pred_class, tf.cast(y_true, tf.int64))
        )
        correct_prediction = tf.cast(correct_prediction, tf.float32)

        self.correct.assign_add(tf.reduce_sum(correct_prediction))
        self.total.assign_add(tf.cast(tf.size(y_true), tf.float32))

    def result(self):
        # avoid division by zero
        return tf.math.divide_no_nan(self.correct, self.total)

    def reset_state(self):
        self.total.assign(0.0)
        self.correct.assign(0.0)

# --------- to switch between # of sensors, also change dense_layer first parameter and keras.Input parameter ----------
# it may also be helpful to switch the number of clusters when clustering weights after training

# # sensor order: left, middle, right
# training_situations = np.array([[0.0, 0.0, 1.0],
#                                 [0.0, 1.0, 0.0],
#                                 [0.0, 1.0, 1.0],
#                                 [1.0, 0.0, 0.0],
#                                 [1.0, 1.0, 0.0],
#                                 [1.0, 1.0, 1.0]], dtype=np.float32)
# # output order: left, straight, right
# training_labels = np.array([2, 1, 2, 0, 0, 1], dtype=np.int32)

# # sensor order: left, middle, right, us
# training_situations = np.array([[0.0, 0.0, 1.0, 0.0],
#                                 [0.0, 1.0, 0.0, 0.0],
#                                 [0.0, 1.0, 1.0, 0.0],
#                                 [1.0, 0.0, 0.0, 0.0],
#                                 [1.0, 1.0, 0.0, 0.0],
#                                 [1.0, 1.0, 1.0, 0.0],
#                                 [0.0, 0.0, 1.0, 1.0],
#                                 [0.0, 1.0, 0.0, 1.0],
#                                 [0.0, 1.0, 1.0, 1.0],
#                                 [1.0, 0.0, 0.0, 1.0],
#                                 [1.0, 1.0, 0.0, 1.0],
#                                 [1.0, 1.0, 1.0, 1.0]], dtype=np.float32)
# # output order: left, straight, right, stop
# training_labels = np.array([2, 1, 2, 0, 0, 1, 3, 3, 3, 3, 3, 3], dtype=np.int32)

# sensor order: LMS, LS, MS, RS, RMS, US
training_situations = np.array([[0.0, 0.0, 0.0, 0.0, 1.0, 0.0],
                                [0.0, 0.0, 0.0, 1.0, 0.0, 0.0],
                                [0.0, 0.0, 0.0, 1.0, 1.0, 0.0],
                                [0.0, 0.0, 1.0, 0.0, 0.0, 0.0],
                                [0.0, 0.0, 1.0, 1.0, 0.0, 0.0],
                                [0.0, 0.0, 1.0, 1.0, 1.0, 0.0],
                                [0.0, 1.0, 0.0, 0.0, 0.0, 0.0],
                                [0.0, 1.0, 1.0, 0.0, 0.0, 0.0],
                                [0.0, 1.0, 1.0, 1.0, 0.0, 0.0],
                                [0.0, 1.0, 1.0, 1.0, 1.0, 0.0],
                                [1.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                                [1.0, 1.0, 0.0, 0.0, 0.0, 0.0],
                                [1.0, 1.0, 1.0, 0.0, 0.0, 0.0],
                                [1.0, 1.0, 1.0, 1.0, 0.0, 0.0],
                                [1.0, 1.0, 1.0, 1.0, 1.0, 0.0],
                                [0.0, 0.0, 0.0, 0.0, 0.0, 1.0],
                                [0.0, 0.0, 0.0, 0.0, 1.0, 1.0],
                                [0.0, 0.0, 0.0, 1.0, 0.0, 1.0],
                                [0.0, 0.0, 0.0, 1.0, 1.0, 1.0],
                                [0.0, 0.0, 1.0, 0.0, 0.0, 1.0],
                                [0.0, 0.0, 1.0, 1.0, 0.0, 1.0],
                                [0.0, 0.0, 1.0, 1.0, 1.0, 1.0],
                                [0.0, 1.0, 0.0, 0.0, 0.0, 1.0],
                                [0.0, 1.0, 1.0, 0.0, 0.0, 1.0],
                                [0.0, 1.0, 1.0, 1.0, 0.0, 1.0],
                                [0.0, 1.0, 1.0, 1.0, 1.0, 1.0],
                                [1.0, 0.0, 0.0, 0.0, 0.0, 1.0],
                                [1.0, 1.0, 0.0, 0.0, 0.0, 1.0],
                                [1.0, 1.0, 1.0, 0.0, 0.0, 1.0],
                                [1.0, 1.0, 1.0, 1.0, 0.0, 1.0],
                                [1.0, 1.0, 1.0, 1.0, 1.0, 1.0]], dtype=np.float32)
# output order: sharp left, left, straight, right, sharp right, stop
# straight > sharp > regular
# training_labels = np.array([4, 3, 4, 2, 2, 2, 1, 2, 2, 2, 0, 0, 2, 2, 2, 5, 5, 5,
#                                 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5], dtype=np.int32)
# straight > regular > sharp
training_labels = np.array([4, 3, 3, 2, 2, 2, 1, 2, 2, 2, 0, 1, 2, 2, 2, 5, 5, 5,
                                5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5], dtype=np.int32)
# sharp > regular > straight
# training_labels = np.array([4, 3, 4, 2, 3, 4, 1, 1, 2, 4, 0, 0, 0, 0, 2, 5, 5, 5,
#                                 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5], dtype=np.int32)

clusteredAccuracy = 0.0
while clusteredAccuracy != 1.0:
    # layer that will do the computation in our model
    dense_layer = keras.layers.Dense(6, kernel_initializer=keras.initializers.RandomUniform(minval=0.01, maxval=1.0),
                                    kernel_constraint=keras.constraints.NonNeg())

    # create and train the model
    model = keras.Sequential(
        [keras.Input((6,)),
        dense_layer]
    )
    model.compile(optimizer='SGD', loss=lambda y_true, y_pred: sparse_ce_with_margin(y_true, y_pred), metrics=[strict_accuracy])
    model.fit(training_situations, training_labels, epochs=100, batch_size=3)

    # cluster the weights into "n_clusters" number of levels
    # so it's easier to translate them into resistances
    new_weights = []
    for w in dense_layer.get_weights():
        if w.ndim > 1:
            flat_w = w.flatten().reshape(-1, 1)
            kmeans = KMeans(n_clusters=6, n_init=10, random_state=42)
            kmeans.fit(flat_w)
            clustered_w = kmeans.cluster_centers_[kmeans.labels_].reshape(w.shape)
            new_weights.append(clustered_w)
        else:
            new_weights.append(w)
    dense_layer.set_weights(new_weights)
    # evaluate to see if we've lost accuracy from the clustering
    loss, clusteredAccuracy = model.evaluate(training_situations, training_labels, verbose=0)
    print("Clustered Accuracy: ", clusteredAccuracy)

    print("Weights:\n", dense_layer.get_weights()[0])
