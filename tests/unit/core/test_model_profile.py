from pytest import raises

from whylogs.core.model_profile import ModelProfile
from whylogs.proto import ModelProfileMessage, ModelType


def test_model_profile():
    mod_prof = ModelProfile()
    assert mod_prof.output_fields == []
    assert mod_prof.metrics is not None
    assert mod_prof.metrics.confusion_matrix is None
    message = mod_prof.to_protobuf()
    ModelProfile.from_protobuf(message)


def test_model_profile_2():
    targets_1 = ["cat", "dog", "pig"]
    predictions_1 = ["cat", "dog", "dog"]
    scores_1 = [0.1, 0.2, 0.4]

    mod_prof = ModelProfile()
    assert scores_1 is not None
    mod_prof.compute_metrics(targets=targets_1, predictions=predictions_1, scores=scores_1)
    assert mod_prof.output_fields == []
    assert mod_prof.metrics is not None
    assert mod_prof.metrics.confusion_matrix is not None
    message = mod_prof.to_protobuf()
    model_profile = ModelProfile.from_protobuf(message)
    assert model_profile.metrics is not None
    assert mod_prof.metrics.confusion_matrix is not None
    assert mod_prof.metrics.confusion_matrix.labels is not None
    assert model_profile.metrics.confusion_matrix.labels == mod_prof.metrics.confusion_matrix.labels


def test_model_profile_infered_type_integers_with_scores_is_classification():
    targets_1 = [1, 2, 2]
    predictions_1 = [219.0, 70.0, 202.0]
    scores_1 = [1, 1, 1]

    mod_prof = ModelProfile()
    mod_prof.compute_metrics(targets_1, predictions_1, scores_1)

    assert mod_prof.metrics is not None
    assert mod_prof.metrics.confusion_matrix is not None
    assert mod_prof.metrics.model_type == ModelType.CLASSIFICATION


def test_model_profile_infered_type_without_scores_is_regression():
    targets_1 = [1, 2, 2]
    predictions_1 = [219.0, 70.0, 202.0]

    mod_prof = ModelProfile()
    mod_prof.compute_metrics(targets_1, predictions_1)

    assert mod_prof.metrics is not None
    assert mod_prof.metrics.confusion_matrix is None
    assert mod_prof.metrics.model_type == ModelType.REGRESSION


def test_model_profile_infered_type_no_change():
    targets_1 = [2, 3, 4]
    predictions_1 = [10.0, 9.0, 8.0]
    scores_1 = [0.9, 0.8, 1]

    mod_prof = ModelProfile()
    assert mod_prof.metrics is not None
    mod_prof.metrics.model_type = ModelType.CLASSIFICATION
    mod_prof.compute_metrics(targets_1, predictions_1, scores_1)
    assert mod_prof.metrics.model_type == ModelType.CLASSIFICATION


def test_merge_profile():
    targets_1 = ["cat", "dog", "pig"]
    predictions_1 = ["cat", "dog", "dog"]
    scores_1 = [0.1, 0.2, 0.4]

    mod_prof = ModelProfile()

    assert mod_prof.output_fields == []
    mod_prof.add_output_field("predictions")

    mod_prof.compute_metrics(targets_1, predictions_1, scores_1)
    assert mod_prof.metrics is not None

    mod_prof_2 = ModelProfile()
    assert mod_prof_2.output_fields == []

    mod_prof_3 = mod_prof.merge(mod_prof_2)
    mod_prof_3.metrics.confusion_matrix
    assert mod_prof_3.output_fields == ["predictions"]


def test_roundtrip_serialization():
    original = ModelProfile(output_fields=["test"])
    serialized_bytes = original.to_protobuf().SerializeToString()
    roundtrip = ModelProfile.from_protobuf(ModelProfileMessage.FromString(serialized_bytes))
    roundtrip.to_protobuf()
    assert roundtrip.output_fields == ["test"]
    assert isinstance(roundtrip.output_fields, list)


def test_merge_profile_nlp():
    targets_1 = ["cat is dog", "cat is dog", "dog is pig"]
    predictions_1 = ["cat is dog", "dog is dog", "dog pig"]

    mod_prof = ModelProfile()
    mod_prof.metrics.model_type = ModelType.NLP

    assert mod_prof.output_fields == []
    mod_prof.add_output_field("monologue")

    with raises(NotImplementedError):
        mod_prof.compute_metrics(targets_1, predictions_1)

    assert mod_prof.metrics is not None

    mod_prof_2 = ModelProfile()
    assert mod_prof_2.output_fields == []

    mod_prof_3 = mod_prof.merge(mod_prof_2)
    assert mod_prof_3.output_fields == ["monologue"]
