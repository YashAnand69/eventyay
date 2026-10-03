import pytest
from django_scopes import scope

from eventyay.base.models import Answer, Submission, TalkQuestion
from eventyay.orga.views.cfp import CfPQuestionRemind


@pytest.mark.django_db
@pytest.mark.parametrize('variant,value', [('date', '2026-10-02'), ('datetime', '2026-10-02T10:30:00+05:30')])
@pytest.mark.parametrize('filled', [True, False])
def test_stored_date_answer_display(event, variant, value, filled):
    with scope(event=event):
        question = TalkQuestion.objects.create(event=event, question='When?', variant=variant)
        answer = Answer.objects.create(question=question, answer=value if filled else '')
        assert answer.answer_string == (value if filled else '')
        assert answer.is_answered == filled


@pytest.mark.django_db
@pytest.mark.parametrize('target', ['submission', 'speaker'])
@pytest.mark.parametrize('variant,value', [('date', '2026-10-02'), ('datetime', '2026-10-02T10:30:00+05:30')])
@pytest.mark.parametrize('filled', [True, False])
def test_date_answer_reminder_eligibility(event, user, target, variant, value, filled):
    with scope(event=event):
        submission = Submission.objects.create(event=event, title='A session', submission_type=event.cfp.default_type)
        submission.speakers.add(user)
        question = TalkQuestion.objects.create(event=event, question='When?', variant=variant, target=target)
        Answer.objects.create(
            question=question,
            answer=value if filled else '',
            submission=submission if target == 'submission' else None,
            person=user if target == 'speaker' else None,
        )
        missing = CfPQuestionRemind.get_missing_answers(
            questions=[question], person=user, submissions=event.submissions.all(),
        )
        assert missing == ([] if filled else [question])
