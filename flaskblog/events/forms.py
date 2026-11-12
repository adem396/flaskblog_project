from flask_wtf import FlaskForm
from wtforms import BooleanField, DateField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, InputRequired, Length, Optional, ValidationError

from flaskblog.models import EVENT_CATEGORIES

MIN_YEAR, MAX_YEAR = 2000, 2100


def _check_year(field):
    if field.data and not (MIN_YEAR <= field.data.year <= MAX_YEAR):
        raise ValidationError(f"Choose a date between {MIN_YEAR} and {MAX_YEAR}.")


class EventForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(max=100)])
    category = SelectField("Type", choices=EVENT_CATEGORIES)
    event_date = DateField("Date", validators=[InputRequired()])
    end_date = DateField("End date (only for events that last several days)", validators=[Optional()])
    description = TextAreaField("Details (optional)", validators=[Optional(), Length(max=1000)])
    is_public = BooleanField("Visible to everyone", default=True)
    submit = SubmitField("Save event")

    def validate_event_date(self, field):
        _check_year(field)

    def validate_end_date(self, field):
        _check_year(field)
        if field.data and self.event_date.data and field.data < self.event_date.data:
            raise ValidationError("The end date can't be before the start date.")
