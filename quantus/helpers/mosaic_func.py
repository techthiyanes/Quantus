"""Collection of mosaic creation functions i..e, group images within a grid structure."""
from typing import List, Tuple, Optional, Union
import random
import math
import numpy as np


def build_single_mosaic(mosaic_images_list: List[np.ndarray]) -> np.ndarray:
    ''' Frame a list of 4 images into a 2x2 mosaic image '''
    first_row = np.concatenate((mosaic_images_list[0], mosaic_images_list[1]), axis=1)
    second_row = np.concatenate((mosaic_images_list[2], mosaic_images_list[3]), axis=1)
    mosaic = np.concatenate((first_row, second_row), axis=2)
    return mosaic


def mosaic_creation(images: np.ndarray, labels: np.ndarray, mosaics_per_class: int, seed: Optional[int] = None) -> \
        Tuple[
            np.ndarray,
            List[Tuple[int, int, int, int]],
            List[Tuple[Union[int, str], ...]],
            List[Tuple[int, int, int, int]],
            List[Union[int, str]]
        ]:
    """

    Parameters
    ----------
    images:
    labels:
    mosaics_per_class:
    seed:

    Returns
    -------


    """
    args = []
    if seed:
        args = [seed]
    rng = random.Random(*args)
    np_rng = np.random.RandomState(*args)

    mosaics_images_list = []
    mosaic_indices_list = []
    mosaic_labels_list = []
    p_batch_list = []
    target_list = []
    total_labels = list(np.unique(labels))

    for target_class in total_labels:
        outer_classes = total_labels.copy()
        outer_classes.remove(target_class)

        target_class_images = images[labels == target_class]
        target_class_image_indices = np.where(labels == target_class)[0]
        target_class_images_and_indices = list(zip(target_class_images, target_class_image_indices))

        no_repetitions = int(math.ceil((2 * mosaics_per_class) / len(target_class_images)))
        total_target_class_images_and_indices = np.repeat(target_class_images_and_indices, repeats=no_repetitions)
        np_rng.shuffle(total_target_class_images_and_indices)

        no_label_repetitions = int(math.ceil((2 * mosaics_per_class) / len(outer_classes)))
        list_outer_images_and_indices = []
        list_outer_classes = []
        for outer_class in outer_classes:
            outer_class_images = images[labels == outer_class]
            outer_class_images_indices = np.where(labels == outer_class)[0]
            outer_class_images_and_indices = list(zip(outer_class_images, outer_class_images_indices))

            list_outer_images_and_indices.append(np_rng.choice(outer_class_images_and_indices, size=no_label_repetitions))
            list_outer_classes.append(np.repeat([outer_class], repeats=no_label_repetitions))

        total_outer_images_and_indices = np.concatenate(list_outer_images_and_indices, axis=0)
        total_outer_labels = np.concatenate(list_outer_classes, axis=0)

        total_outer = list(zip(total_outer_images_and_indices.tolist(), total_outer_labels.tolist()))
        rng.shuffle(total_outer)

        iter_images_and_indices = iter(total_target_class_images_and_indices)
        iter_outer = iter(total_outer)
        for _ in range(mosaics_per_class):
            mosaic_elems = [
                (next(iter_images_and_indices), target_class), (next(iter_images_and_indices), target_class),
                next(iter_outer), next(iter_outer)
            ]
            rng.shuffle(mosaic_elems)

            current_mosaic = build_single_mosaic([elem[0][0] for elem in mosaic_elems])
            mosaics_images_list.append(current_mosaic)

            mosaic_indices = tuple(elem[0][1] for elem in mosaic_elems)
            mosaic_indices_list.append(mosaic_indices)

            current_targets = tuple(elem[1] for elem in mosaic_elems)
            mosaic_labels_list.append(current_targets)

            current_p_batch = tuple(int(elem[1] == target_class) for elem in mosaic_elems)
            p_batch_list.append(current_p_batch)

            target_list.append(target_class)

    all_mosaics = np.array(mosaics_images_list)

    return all_mosaics, mosaic_indices_list, mosaic_labels_list, p_batch_list, target_list
