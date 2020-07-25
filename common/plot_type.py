from enum import Enum

class PlotType:

    class TrainedModel(Enum):

        ground_truth_versus_prediction = 1

        date_versus_ground_truth_and_prediction_for_training_and_testing_dataset = 2


