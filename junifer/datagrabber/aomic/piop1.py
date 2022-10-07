"""Provide concrete implementations for AOMICPIOP1 data access."""

# Authors: Federico Raimondo <f.raimondo@fz-juelich.de>
#          Vera Komeyer <v.komeyer@fz-juelich.de>
#          Xuan Li <xu.li@fz-juelich.de>
#          Leonard Sasse <l.sasse@fz-juelich.de>
# License: AGPL

from itertools import product
from pathlib import Path
from typing import Dict, List, Tuple, Union

from junifer.datagrabber import PatternDataladDataGrabber

from ...api.decorators import register_datagrabber
from ...utils import raise_error


@register_datagrabber
class DataladAOMICPIOP1(PatternDataladDataGrabber):
    """Concrete implementation for pattern-based data fetching of AOMICPIOP1.

    Parameters
    ----------
    datadir : str or Path, optional
        The directory where the datalad dataset will be cloned. If None,
        the datalad dataset will be cloned into a temporary directory
        (default None).
    tasks : {"restingstate", "anticipation", "emomatching", "faces", "gstroop",
        "workingmemory"} or list of the options, optional
        AOMIC PIOP1 task sessions. If None, all available task sessions are
        selected (default None).
    **kwargs
        Keyword arguments passed to superclass.

    """

    def __init__(
        self,
        datadir: Union[str, Path, None] = None,
        tasks: Union[str, List[str], None] = None,
        **kwargs,
    ) -> None:
        """Initialize the class."""
        # The types of data
        types = [
            "BOLD",
            "BOLD_confounds",
            "T1w",
            "probseg_CSF",
            "probseg_GM",
            "probseg_WM",
            "DWI",
        ]

        if isinstance(tasks, str):
            tasks = [tasks]

        all_tasks = [
            "restingstate",
            "anticipation",
            "emomatching",
            "faces",
            "gstroop",
            "workingmemory",
        ]

        if tasks is None:
            tasks = all_tasks
        else:
            for t in tasks:
                if t not in all_tasks:
                    raise_error(
                        f"{t} is not a valid task in the AOMIC PIOP1"
                        " dataset!"
                    )

        self.tasks = tasks

        patterns = {
            "BOLD": (
                "derivatives/fmriprep/sub-{subject}/func/"
                "sub-{subject}_task-{task}_"
                "space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz"
            ),
            "BOLD_confounds": (
                "derivatives/fmriprep/sub-{subject}/func/"
                "sub-{subject}_task-{task}_"
                "desc-confounds_regressors.tsv"
            ),
            "T1w": (
                "derivatives/fmriprep/sub-{subject}/anat/"
                "sub-{subject}_space-MNI152NLin2009cAsym_"
                "desc-preproc_T1w.nii.gz"
            ),
            "probseg_CSF": (
                "derivatives/fmriprep/sub-{subject}/anat/"
                "sub-{subject}_space-MNI152NLin2009cAsym_label-"
                "CSF_probseg.nii.gz"
            ),
            "probseg_GM": (
                "derivatives/fmriprep/sub-{subject}/anat/"
                "sub-{subject}_space-MNI152NLin2009cAsym_label-"
                "GM_probseg.nii.gz"
            ),
            "probseg_WM": (
                "derivatives/fmriprep/sub-{subject}/anat/"
                "sub-{subject}_space-MNI152NLin2009cAsym_label-"
                "WM_probseg.nii.gz"
            ),
            "DWI": (
                "derivatives/dwipreproc/sub-{subject}/dwi/"
                "sub-{subject}_desc-preproc_dwi.nii.gz"
            ),
        }
        uri = "https://github.com/OpenNeuroDatasets/ds002785"
        replacements = ["subject", "task"]
        super().__init__(
            types=types,
            datadir=datadir,
            uri=uri,
            patterns=patterns,
            replacements=replacements,
        )

    def __getitem__(self, element: Tuple[str, str]) -> Dict[str, Path]:
        """Index one element in the dataset.

        Parameters
        ----------
        element : tuple of str
            The element to be indexed. First element in the tuple is the
            subject, second element is the task.

        Returns
        -------
        out : dict
            Dictionary of paths for each type of data required for the
            specified element.

        """
        sub, task = element

        # depending on task 'acquisition is different'
        task_acqs = {
            "anticipation": "seq",
            "emomatching": "seq",
            "faces": "mb3",
            "gstroop": "seq",
            "restingstate": "mb3",
            "workingmemory": "seq",
        }
        acq = task_acqs[task]
        new_task = f"{task}_acq-{acq}"

        out = super().__getitem__((sub, new_task))
        out["meta"]["element"] = {"subject": sub, "task": task}
        return out

    def get_elements(self) -> List:
        """Implement fetching list of subjects in the dataset.

        Returns
        -------
        elements : list of str
            The list of subjects in the dataset.

        """
        subjects = [f"{x:04d}" for x in range(1, 217)]
        elems = []
        for subject, task in product(subjects, self.tasks):
            elems.append((subject, task))

        return elems