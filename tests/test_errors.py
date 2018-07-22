import pytest
from excelcy import ExcelCy
from excelcy.errors import Errors
from tests.test_base import BaseTestCase


class TestErrors(BaseTestCase):
    def test_e001(self):
        """ Test: Error code E001 """

        with pytest.raises(ValueError) as excinfo:
            excelcy = ExcelCy()
            excelcy.load(file_path='not_exist.xlsx')

        assert str(excinfo.value) == Errors.E001
