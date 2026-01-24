from enum import Enum

_SUBJECT_LABELS = {
    "HV": "habilidad-verbal",
    "HM": "habilidad-matematica",
    "AR": "aritmetica",
    "AL": "algebra",
    "GE": "geometria",
    "TR": "trigonometria",
    "LE": "lenguaje",
    "LI": "literatura",
    "PS": "psicologia",
    "EC": "educacion-civica",
    "HP": "historia-peru",
    "HU": "historia-universal",
    "GG": "geografia",
    "EO": "economia",
    "FI": "filosofia",
    "FS": "fisica",
    "QU": "quimica",
    "BI": "biologia",
}


class SubjectCode(str, Enum):
    HV = "HV"
    HM = "HM"
    AR = "AR"
    AL = "AL"
    GE = "GE"
    TR = "TR"
    LE = "LE"
    LI = "LI"
    PS = "PS"
    EC = "EC"
    HP = "HP"
    HU = "HU"
    GG = "GG"
    EO = "EO"
    FI = "FI"
    FS = "FS"
    QU = "QU"
    BI = "BI"

    @property
    def label(self) -> str:
        return _SUBJECT_LABELS[self.value]
