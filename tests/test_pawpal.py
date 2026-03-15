from pawpal_system import CareTask, Pet


def test_mark_complete_changes_status():
    task = CareTask(
        title="Morning walk",
        duration_minutes=30,
        priority="high",
        task_type="exercise",
    )
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_count():
    pet = Pet(name="Mochi", species="dog")
    assert len(pet.tasks) == 0

    pet.add_task(CareTask(
        title="Feed breakfast",
        duration_minutes=10,
        priority="high",
        task_type="feeding",
    ))
    assert len(pet.tasks) == 1

    pet.add_task(CareTask(
        title="Brush fur",
        duration_minutes=15,
        priority="low",
        task_type="grooming",
    ))
    assert len(pet.tasks) == 2
