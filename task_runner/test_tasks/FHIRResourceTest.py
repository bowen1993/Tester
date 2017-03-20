from ..abstract_test_task import abstract_test_task

class FHIRResourceTest(abstract_test_task):
    def __init__(self, task_id, runner_obj, resources=[]):
        super.__init__(task_id, runner_obj)
        self.resources = resources

