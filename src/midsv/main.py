from __future__ import annotations

from pathlib import Path

from midsv import convert, format, io, validate
from midsv.proofread import polish


def transform(
    path_sam: Path | str,
    qscore: bool = False,
    keep: str | list[str] = None,
) -> list[dict[str, str | int]]:
    """Integrated function to perform MIDSV conversion.

    Args:
        path_sam (str | Path): Path of a SAM file.
        qscore (bool, optional): Output QSCORE. Defaults to False.
        keep (str | list[str], optional): Subset of 'FLAG', 'POS', 'CIGAR', 'SEQ', 'QUAL', 'CSTAG' to keep. Defaults to None.

    Returns:
        list[dict[str, str]]: Dictionary containing QNAME, RNAME, MIDSV, QSCORE, and fields specified by the keep argument.
    """

    keep = validate.keep_argument(keep)

    path_sam = Path(path_sam)
    validate.sam_headers(io.read_sam(path_sam))
    validate.sam_alignments(io.read_sam(path_sam), qscore)

    sqheaders: dict[str, str | int] = format.extract_sqheaders(io.read_sam(path_sam))
    samdict: list[dict[str, str | int]] = format.dictionarize_sam(io.read_sam(path_sam))

    samdict = format.remove_softclips(samdict)
    samdict = format.remove_resequence(samdict)

    for alignment in samdict:
        alignment["MIDSV"] = convert.cstag_to_midsv(alignment["CSTAG"])
        if qscore:
            alignment["QSCORE"] = convert.qual_to_qscore(alignment["QUAL"], alignment["MIDSV"])

    samdict_polished = polish(samdict, sqheaders, keep)

    return samdict_polished
