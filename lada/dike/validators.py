import re
import logging
from collections import defaultdict

import lada.models

from wtforms import ValidationError

from lada.dike import maintenance

log = logging.getLogger(__name__)


def logged_validation_error(message):
    log.debug(message)
    raise ValidationError(message)


class ReckoningFieldValidator:
    def __init__(self, position, maximum=1):
        self.position = position
        self.maximum = maximum

    def __call__(self, form, field):
        if field.data is None:
            return

        match = re.match(r"^\d+(\+\d+)*$", field.data)
        if not match:
            logged_validation_error("Invalid request format")

        fellows = [int(k) for k in field.data.split("+")]
        if self.maximum is not None and len(fellows) > self.maximum:
            logged_validation_error(f"Maximal number of candidates for {self.position} exceeded: {self.maximum}")

        election = maintenance.get_election()
        position = election.positions.filter_by(name=self.position).first()

        for fellow_id in fellows:
            if position.elected.filter_by(id=fellow_id).scalar() is None:
                fellow = lada.models.Fellow.query.filter_by(id=fellow_id).first()
                logged_validation_error(f"Fellow {str(fellow)} is not elected for position {self.position}")


class ReckoningMaxFellowValidator:
    def __init__(self, maximum, positions):
        self.maximum = maximum
        self.positions = positions

    def __call__(self, form, field):
        candidates_count = 0

        for position in self.positions:
            position_field = getattr(form, position)
            if position_field.data is None:
                continue

            fellows = position_field.data.split("+")
            candidates_count += len(fellows)

        if candidates_count > self.maximum:
            logged_validation_error(f"Total maximal number of fellows exceeded: {self.maximum}")


class ReckoningNoDuplicatesValidator:
    def __init__(self, positions):
        self.positions = positions

    def __call__(self, form, field):
        candidates = []

        for position in self.positions:
            position_field = getattr(form, position)
            if position_field.data is None:
                continue

            fellows = position_field.data.split("+")
            candidates.extend(fellows)

        if len(candidates) != len(set(candidates)):
            logged_validation_error("Candidate duplicate detected")


class DynamicBallotDuplicateDetector:
    def __init__(self):
        pass

    def __call__(self, form, field):
        votes = defaultdict(list)
        for field in form.data:
            if "+" in field:
                name = field.split("+")
                rank = form.data[field]
                if rank not in ("n", "x"):
                    votes[int(name[0])].append(rank)

        for key in votes:
            if len(votes[key]) != len(set(votes[key])):
                logged_validation_error("Ballot rank duplicate detected")


class RegisterMandatoryPositionValidator:
    def __init__(self, reasons):
        self.reasons = reasons

    def __call__(self, form, field):
        if not field.data:
            for position_name in self.reasons:
                position = getattr(form, position_name)

                if position.data:
                    logged_validation_error(f"Candidacy is mandatory when candidating for any of {self.reasons}")
