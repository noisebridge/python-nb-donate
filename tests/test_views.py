import pytest
import git


def validate_main_page_data(data):
    assert "donation-form" in data
    assert 'charge[amount]' in data
    assert 'cc-number' in data
    assert 'data-stripe' in data
    assert 'cc-exp' in data
    assert 'cvc' in data
    assert 'charge[recurring]' in data
    assert 'donor[email]' in data
    assert 'donation-form-name' in data
    assert 'donation-form-anonymous' in data
    assert 'donor[anonymous]' in data
    assert 'donor[name]' in data
    assert 'bitcoin' in data


def test_view_main(testapp):
    app = testapp
    result = app.get('/')
    assert result.status_code == 200
    data = result.data.decode('utf-8')
    validate_main_page_data(data)

    result = app.get('/index')
    assert result.status_code == 200
    data = result.data.decode('utf-8')
    validate_main_page_data(data)


def test_view_thanks(testapp):
    app = testapp

    result = app.get('/thanks')

    data = result.data.decode('utf-8')
    assert result.status_code == 200
    assert "humbled" in data
    assert "thankful" in data


def test_view_new_project_get(testapp):
    app = testapp

    result = app.get('/new/project')
    assert result.status_code == 200
    data = result.data.decode('utf-8')
    assert '<form action="/new/project" method="POST">' in data
    assert "Project Name" in data
    assert '<input class="project-name"' in data
    assert "Goal" in data
    assert '<input class="project-goal"' in data
    assert "Currency" in data
    assert '<input class="project-currency"' in data
    assert "Description" in data
    assert '<input class="project-description' in data
    assert '<input type="submit"' in data


def test_view_new_project_post(testapp):
    pass
