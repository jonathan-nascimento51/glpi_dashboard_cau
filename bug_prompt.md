# Identidade
Você é um assistente de depuração para o projeto GLPI Dashboard.

## Instruções
Analise os erros abaixo e sugira correções de código mantendo o estilo do projeto.

## Erros e avisos
### pytest
```

==================================== ERRORS ====================================
_____________ ERROR collecting tests/integration/test_dashboard.py _____________
ImportError while importing test module '/workspace/glpi_dashboard_cau/tests/integration/test_dashboard.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/root/.pyenv/versions/3.12.10/lib/python3.12/importlib/__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests/integration/test_dashboard.py:13: in <module>
    main_globals = runpy.run_path(str(ROOT / "main.py"))
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
main.py:10: in <module>
    from glpi_dashboard.config.settings import (
E   ModuleNotFoundError: No module named 'glpi_dashboard'
__________________ ERROR collecting tests/test_batch_fetch.py __________________
ImportError while importing test module '/workspace/glpi_dashboard_cau/tests/test_batch_fetch.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/root/.pyenv/versions/3.12.10/lib/python3.12/importlib/__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests/test_batch_fetch.py:7: in <module>
    from glpi_dashboard.services import batch_fetch
E   ModuleNotFoundError: No module named 'glpi_dashboard'
________________ ERROR collecting tests/test_circuit_breaker.py ________________
ImportError while importing test module '/workspace/glpi_dashboard_cau/tests/test_circuit_breaker.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/root/.pyenv/versions/3.12.10/lib/python3.12/importlib/__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests/test_circuit_breaker.py:1: in <module>
    from patterns.resilience.circuit_breaker import breaker, call_with_breaker
E   ModuleNotFoundError: No module named 'patterns'
_________________ ERROR collecting tests/test_data_pipeline.py _________________
ImportError while importing test module '/workspace/glpi_dashboard_cau/tests/test_data_pipeline.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/root/.pyenv/versions/3.12.10/lib/python3.12/importlib/__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests/test_data_pipeline.py:6: in <module>
    from glpi_dashboard.data import transform
E   ModuleNotFoundError: No module named 'glpi_dashboard'
_______________ ERROR collecting tests/test_dishka_container.py ________________
ImportError while importing test module '/workspace/glpi_dashboard_cau/tests/test_dishka_container.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/root/.pyenv/versions/3.12.10/lib/python3.12/importlib/__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests/test_dishka_container.py:6: in <module>
    from app.domain.entities.order import Order
E   ModuleNotFoundError: No module named 'app'
_________________ ERROR collecting tests/test_fetch_tickets.py _________________
ImportError while importing test module '/workspace/glpi_dashboard_cau/tests/test_fetch_tickets.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/root/.pyenv/versions/3.12.10/lib/python3.12/importlib/__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests/test_fetch_tickets.py:5: in <module>
    import scripts.fetch_tickets as fetch_tickets
scripts/fetch_tickets.py:10: in <module>
    from glpi_dashboard.services.glpi_api_client import GlpiApiClient
E   ModuleNotFoundError: No module named 'glpi_dashboard'
________________ ERROR collecting tests/test_glpi_api_client.py ________________
ImportError while importing test module '/workspace/glpi_dashboard_cau/tests/test_glpi_api_client.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/root/.pyenv/versions/3.12.10/lib/python3.12/importlib/__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests/test_glpi_api_client.py:6: in <module>
    from glpi_dashboard.services.exceptions import (
E   ModuleNotFoundError: No module named 'glpi_dashboard'
__________________ ERROR collecting tests/test_glpi_client.py __________________
ImportError while importing test module '/workspace/glpi_dashboard_cau/tests/test_glpi_client.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/root/.pyenv/versions/3.12.10/lib/python3.12/importlib/__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests/test_glpi_client.py:5: in <module>
    from glpi_dashboard.services.glpi_rest_client import GLPIClient
E   ModuleNotFoundError: No module named 'glpi_dashboard'
__________________ ERROR collecting tests/test_glpi_errors.py __________________
ImportError while importing test module '/workspace/glpi_dashboard_cau/tests/test_glpi_errors.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/root/.pyenv/versions/3.12.10/lib/python3.12/importlib/__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests/test_glpi_errors.py:9: in <module>
    from glpi_dashboard.logging_config import setup_logging
E   ModuleNotFoundError: No module named 'glpi_dashboard'
_______________ ERROR collecting tests/test_glpi_rest_client.py ________________
ImportError while importing test module '/workspace/glpi_dashboard_cau/tests/test_glpi_rest_client.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/root/.pyenv/versions/3.12.10/lib/python3.12/importlib/__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests/test_glpi_rest_client.py:6: in <module>
    from glpi_dashboard.services.glpi_rest_client import GLPIClient
E   ModuleNotFoundError: No module named 'glpi_dashboard'
_________________ ERROR collecting tests/test_glpi_session.py __________________
ImportError while importing test module '/workspace/glpi_dashboard_cau/tests/test_glpi_session.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/root/.pyenv/versions/3.12.10/lib/python3.12/importlib/__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests/test_glpi_session.py:12: in <module>
    from glpi_dashboard.logging_config import setup_logging
E   ModuleNotFoundError: No module named 'glpi_dashboard'
________________ ERROR collecting tests/test_graphql_client.py _________________
ImportError while importing test module '/workspace/glpi_dashboard_cau/tests/test_graphql_client.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/root/.pyenv/versions/3.12.10/lib/python3.12/importlib/__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests/test_graphql_client.py:1: in <module>
    from glpi_dashboard.services.graphql_client import GlpiGraphQLClient
E   ModuleNotFoundError: No module named 'glpi_dashboard'
______________ ERROR collecting tests/test_langgraph_workflow.py _______________
ImportError while importing test module '/workspace/glpi_dashboard_cau/tests/test_langgraph_workflow.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/root/.pyenv/versions/3.12.10/lib/python3.12/importlib/__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests/test_langgraph_workflow.py:3: in <module>
    from glpi_dashboard.services import langgraph_workflow
E   ModuleNotFoundError: No module named 'glpi_dashboard'
_____________________ ERROR collecting tests/test_money.py _____________________
ImportError while importing test module '/workspace/glpi_dashboard_cau/tests/test_money.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/root/.pyenv/versions/3.12.10/lib/python3.12/importlib/__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests/test_money.py:5: in <module>
    from app.domain.value_objects.money import Money
E   ModuleNotFoundError: No module named 'app'
_____________________ ERROR collecting tests/test_order.py _____________________
ImportError while importing test module '/workspace/glpi_dashboard_cau/tests/test_order.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/root/.pyenv/versions/3.12.10/lib/python3.12/importlib/__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests/test_order.py:4: in <module>
    from app.domain.entities.order import Order
E   ModuleNotFoundError: No module named 'app'
_________________ ERROR collecting tests/test_redis_client.py __________________
ImportError while importing test module '/workspace/glpi_dashboard_cau/tests/test_redis_client.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/root/.pyenv/versions/3.12.10/lib/python3.12/importlib/__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests/test_redis_client.py:6: in <module>
    from glpi_dashboard.utils.redis_client import RedisClient
E   ModuleNotFoundError: No module named 'glpi_dashboard'
_________________ ERROR collecting tests/test_sanitization.py __________________
ImportError while importing test module '/workspace/glpi_dashboard_cau/tests/test_sanitization.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/root/.pyenv/versions/3.12.10/lib/python3.12/importlib/__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests/test_sanitization.py:7: in <module>
    from glpi_dashboard.dashboard.components import compute_ticket_stats
E   ModuleNotFoundError: No module named 'glpi_dashboard'
__________________ ERROR collecting tests/test_schema_path.py __________________
ImportError while importing test module '/workspace/glpi_dashboard_cau/tests/test_schema_path.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/root/.pyenv/versions/3.12.10/lib/python3.12/importlib/__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests/test_schema_path.py:1: in <module>
    from glpi_dashboard.data.database import SCHEMA_FILE
E   ModuleNotFoundError: No module named 'glpi_dashboard'
_____________ ERROR collecting tests/test_sqlalchemy_repository.py _____________
ImportError while importing test module '/workspace/glpi_dashboard_cau/tests/test_sqlalchemy_repository.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/root/.pyenv/versions/3.12.10/lib/python3.12/importlib/__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests/test_sqlalchemy_repository.py:7: in <module>
    from app.infrastructure.persistence.sqlalchemy_repository import (
E   ModuleNotFoundError: No module named 'app'
________________ ERROR collecting tests/test_tickets_groups.py _________________
ImportError while importing test module '/workspace/glpi_dashboard_cau/tests/test_tickets_groups.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/root/.pyenv/versions/3.12.10/lib/python3.12/importlib/__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests/test_tickets_groups.py:6: in <module>
    from glpi_dashboard.data import tickets_groups
E   ModuleNotFoundError: No module named 'glpi_dashboard'
___________________ ERROR collecting tests/test_transform.py ___________________
ImportError while importing test module '/workspace/glpi_dashboard_cau/tests/test_transform.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/root/.pyenv/versions/3.12.10/lib/python3.12/importlib/__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests/test_transform.py:6: in <module>
    from glpi_dashboard.data import transform
E   ModuleNotFoundError: No module named 'glpi_dashboard'
_________________ ERROR collecting tests/test_user_service.py __________________
ImportError while importing test module '/workspace/glpi_dashboard_cau/tests/test_user_service.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/root/.pyenv/versions/3.12.10/lib/python3.12/importlib/__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests/test_user_service.py:1: in <module>
    from app.application.commands.user_service import Credentials, UserService
E   ModuleNotFoundError: No module named 'app'
__________________ ERROR collecting tests/test_worker_api.py ___________________
ImportError while importing test module '/workspace/glpi_dashboard_cau/tests/test_worker_api.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/root/.pyenv/versions/3.12.10/lib/python3.12/importlib/__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests/test_worker_api.py:5: in <module>
    from glpi_dashboard.services.exceptions import GLPIUnauthorizedError
E   ModuleNotFoundError: No module named 'glpi_dashboard'
=========================== short test summary info ============================
ERROR tests/integration/test_dashboard.py
ERROR tests/test_batch_fetch.py
ERROR tests/test_circuit_breaker.py
ERROR tests/test_data_pipeline.py
ERROR tests/test_dishka_container.py
ERROR tests/test_fetch_tickets.py
ERROR tests/test_glpi_api_client.py
ERROR tests/test_glpi_client.py
ERROR tests/test_glpi_errors.py
ERROR tests/test_glpi_rest_client.py
ERROR tests/test_glpi_session.py
ERROR tests/test_graphql_client.py
ERROR tests/test_langgraph_workflow.py
ERROR tests/test_money.py
ERROR tests/test_order.py
ERROR tests/test_redis_client.py
ERROR tests/test_sanitization.py
ERROR tests/test_schema_path.py
ERROR tests/test_sqlalchemy_repository.py
ERROR tests/test_tickets_groups.py
ERROR tests/test_transform.py
ERROR tests/test_user_service.py
ERROR tests/test_worker_api.py
!!!!!!!!!!!!!!!!!!! Interrupted: 23 errors during collection !!!!!!!!!!!!!!!!!!!
1 deselected, 23 errors in 6.89s

```
### flake8
```
./frontend/node_modules/flatted/python/flatted.py:19:1: E302 expected 2 blank lines, found 1
./frontend/node_modules/flatted/python/flatted.py:24:1: E302 expected 2 blank lines, found 1
./frontend/node_modules/flatted/python/flatted.py:37:1: E302 expected 2 blank lines, found 1
./frontend/node_modules/flatted/python/flatted.py:43:1: E302 expected 2 blank lines, found 1
./frontend/node_modules/flatted/python/flatted.py:46:1: E302 expected 2 blank lines, found 1
./frontend/node_modules/flatted/python/flatted.py:49:1: E302 expected 2 blank lines, found 1
./frontend/node_modules/flatted/python/flatted.py:52:1: E302 expected 2 blank lines, found 1
./frontend/node_modules/flatted/python/flatted.py:59:1: E302 expected 2 blank lines, found 1
./frontend/node_modules/flatted/python/flatted.py:67:1: E302 expected 2 blank lines, found 1
./frontend/node_modules/flatted/python/flatted.py:77:1: E302 expected 2 blank lines, found 1
./frontend/node_modules/flatted/python/flatted.py:81:9: E722 do not use bare 'except'
./frontend/node_modules/flatted/python/flatted.py:86:1: E302 expected 2 blank lines, found 1
./frontend/node_modules/flatted/python/flatted.py:101:1: E302 expected 2 blank lines, found 1
./frontend/node_modules/flatted/python/flatted.py:117:1: E302 expected 2 blank lines, found 1
./src/glpi_dashboard/services/glpi_session.py:62:89: E501 line too long (90 > 88 characters)
./tests/e2e/test_flow.py:8:1: E402 module level import not at top of file
./tests/test_data_pipeline.py:4:1: E402 module level import not at top of file
./tests/test_data_pipeline.py:6:1: E402 module level import not at top of file
./tests/test_data_pipeline.py:7:1: E402 module level import not at top of file
./tests/test_filters.py:5:1: E402 module level import not at top of file
./tests/test_filters.py:7:1: E402 module level import not at top of file
./tests/test_glpi_client.py:11:89: E501 line too long (96 > 88 characters)
./tests/test_glpi_errors.py:7:1: E402 module level import not at top of file
./tests/test_glpi_errors.py:9:1: E402 module level import not at top of file
./tests/test_glpi_errors.py:10:1: E402 module level import not at top of file
./tests/test_glpi_session.py:10:1: E402 module level import not at top of file
./tests/test_glpi_session.py:12:1: E402 module level import not at top of file
./tests/test_glpi_session.py:13:1: E402 module level import not at top of file
./tests/test_glpi_session.py:14:1: E402 module level import not at top of file
./tests/test_sanitization.py:5:1: E402 module level import not at top of file
./tests/test_sanitization.py:7:1: E402 module level import not at top of file
./tests/test_sanitization.py:8:1: E402 module level import not at top of file
./tests/test_transform.py:4:1: E402 module level import not at top of file
./tests/test_transform.py:6:1: E402 module level import not at top of file

```
### merge_conflicts
```
frontend/node_modules/debounce/History.md: conflict markers at lines 3, 8, 13, 18, 27, 32, 43, 48, 53
frontend/node_modules/jsonfile/README.md: conflict markers at lines 2
frontend/node_modules/wcwidth/LICENSE: conflict markers at lines 2
frontend/node_modules/string.prototype.matchall/CHANGELOG.md: conflict markers at lines 95, 104, 116, 123, 133, 138, 151, 159, 168, 177
frontend/node_modules/object-keys/CHANGELOG.md: conflict markers at lines 2, 6, 14, 18, 22, 31, 36, 44, 51, 57, 63, 69, 73, 79, 83, 87, 94, 102, 108, 116, 135, 154, 160, 172, 178, 184, 191, 196, 202, 209, 225
frontend/node_modules/mime-db/HISTORY.md: conflict markers at lines 2, 10, 17, 23, 29, 36, 43, 51, 63, 70, 78, 85, 92, 98, 104, 112, 118, 125, 132, 141, 149, 156, 166, 179, 187, 194, 200, 206, 211, 217, 223, 232, 238, 244, 250, 255, 263, 268, 273, 281, 297, 305, 314, 321, 327, 335, 343, 349, 354, 367, 377, 427, 434, 456, 465, 470, 475, 480, 485, 495, 500
frontend/node_modules/http-proxy-agent/README.md: conflict markers at lines 2
frontend/node_modules/array.prototype.flatmap/CHANGELOG.md: conflict markers at lines 42, 50, 60, 71, 80, 89, 95, 104, 111, 117, 121
frontend/node_modules/https-proxy-agent/README.md: conflict markers at lines 2
frontend/node_modules/es-to-primitive/CHANGELOG.md: conflict markers at lines 54, 65, 74, 78, 89, 100
frontend/node_modules/caniuse-lite/LICENSE: conflict markers at lines 3, 55, 376
frontend/node_modules/lz-string/README.md: conflict markers at lines 2
frontend/node_modules/deep-is/README.markdown: conflict markers at lines 2, 15, 32, 43, 61
frontend/node_modules/w3c-xmlserializer/LICENSE.md: conflict markers at lines 2
frontend/node_modules/semver/README.md: conflict markers at lines 2
frontend/node_modules/argparse/LICENSE: conflict markers at lines 2, 60
frontend/node_modules/argparse/README.md: conflict markers at lines 2
frontend/node_modules/js-yaml/README.md: conflict markers at lines 2
frontend/node_modules/mime-types/HISTORY.md: conflict markers at lines 2, 11, 17, 24, 31, 38, 46, 55, 68, 76, 85, 93, 100, 107, 115, 122, 130, 140, 153, 167, 177, 184, 190, 196, 203, 209, 217, 223, 229, 235, 241, 247, 253, 259, 265, 270, 285, 291, 297, 303, 309, 315, 322, 328, 335, 343, 349, 355, 361, 368, 373, 379, 384, 389, 395
frontend/node_modules/js-tokens/README.md: conflict markers at lines 2, 17, 74, 86, 113, 238
frontend/node_modules/es-abstract/CHANGELOG.md: conflict markers at lines 2, 12, 61, 71, 76, 84, 109, 113, 124, 134, 143, 149, 161, 175, 191, 198, 209, 213, 234, 254, 290, 307, 338, 346, 351, 357, 365, 372, 383, 388, 392, 402, 425, 430, 445, 452, 461, 466, 473, 477, 481, 494, 505, 541, 564, 577, 594, 602, 626, 632, 637, 642, 646, 652, 665, 670, 674, 679, 685, 696, 708, 723, 728, 732, 769, 784, 790, 796, 803, 811, 816, 823, 842, 850, 854, 861, 871, 878, 885, 889, 897, 904, 910, 914, 921, 927, 931, 936, 940, 945, 951, 956
frontend/node_modules/eslint-plugin-react/README.md: conflict markers at lines 3
frontend/node_modules/define-properties/CHANGELOG.md: conflict markers at lines 30, 49, 58, 65, 71, 77, 81, 86, 90
frontend/node_modules/util-deprecate/README.md: conflict markers at lines 2
frontend/node_modules/util-deprecate/History.md: conflict markers at lines 3, 8, 14
frontend/node_modules/async-lock/History.md: conflict markers at lines 2, 6, 11, 15, 19, 23, 27, 31, 36, 40, 45, 49, 54, 58, 62, 66, 70, 74, 78, 82, 86, 94, 98, 102, 106, 110, 114, 118, 122, 126, 131
frontend/node_modules/typescript/ThirdPartyNoticeText.txt: conflict markers at lines 105
frontend/node_modules/playwright-core/ThirdPartyNotices.txt: conflict markers at lines 53, 55, 199, 203, 225, 229, 251, 255, 275, 279, 301, 305, 331, 335, 358, 362, 381, 385, 405, 409, 429, 433, 443, 447, 477, 481, 505, 509, 531, 535, 545, 549, 565, 569, 571, 707, 711, 731, 735, 745, 749, 759, 763, 789, 793, 834, 838, 860, 864, 880, 884, 906, 910, 932, 936, 952, 956, 966, 970, 994, 998, 1019, 1023, 1046, 1050, 1071, 1075, 1097, 1101, 1123, 1127, 1144, 1148, 1169, 1173, 1175, 1326, 1330, 1351, 1355, 1380, 1384, 1400, 1404, 1425, 1429, 1443, 1447, 1469, 1473, 1495, 1499, 1501
frontend/node_modules/thenify/History.md: conflict markers at lines 3, 9
frontend/node_modules/object.fromentries/CHANGELOG.md: conflict markers at lines 39, 50, 58, 69, 78, 86, 91
frontend/node_modules/imurmurhash/README.md: conflict markers at lines 2
frontend/node_modules/function.prototype.name/CHANGELOG.md: conflict markers at lines 61, 69, 80, 91, 101, 114, 121, 126, 130, 140
frontend/node_modules/array-includes/CHANGELOG.md: conflict markers at lines 49, 57, 68, 77, 88, 96, 114, 122, 132, 136, 145, 149, 154, 158, 164, 168, 172, 178, 182, 186
frontend/node_modules/is-typed-array/CHANGELOG.md: conflict markers at lines 67, 77, 83, 88, 97, 103, 115, 119, 124, 134, 145, 152, 156, 161, 165
frontend/node_modules/array.prototype.flat/CHANGELOG.md: conflict markers at lines 38, 46, 57, 68, 78, 86, 92, 101, 108, 114, 118
frontend/node_modules/base64-js/README.md: conflict markers at lines 2
frontend/node_modules/streamsearch/README.md: conflict markers at lines 2, 10, 16, 21
frontend/node_modules/concat-map/README.markdown: conflict markers at lines 2, 11, 29, 46, 55
frontend/node_modules/object.assign/CHANGELOG.md: conflict markers at lines 2, 6, 15, 23, 27, 47, 54, 69, 77, 86, 96, 103, 107, 119, 128, 134, 142, 151, 155, 165, 169, 174, 178, 186, 190, 194, 198, 202, 206, 210, 220, 224, 230, 236, 240, 244
frontend/node_modules/playwright/ThirdPartyNotices.txt: conflict markers at lines 145, 347, 351, 374, 378, 401, 405, 428, 432, 455, 459, 482, 486, 509, 513, 536, 540, 563, 567, 590, 594, 617, 621, 644, 648, 671, 675, 698, 702, 725, 729, 752, 756, 779, 783, 806, 810, 833, 837, 860, 864, 887, 891, 914, 918, 938, 942, 965, 969, 992, 996, 1019, 1023, 1046, 1050, 1073, 1077, 1100, 1104, 1127, 1131, 1154, 1158, 1181, 1185, 1208, 1212, 1235, 1239, 1262, 1266, 1289, 1293, 1316, 1320, 1343, 1347, 1370, 1374, 1397, 1401, 1424, 1428, 1451, 1455, 1478, 1482, 1505, 1509, 1532, 1536, 1559, 1563, 1586, 1590, 1613, 1617, 1640, 1644, 1666, 1670, 1692, 1696, 1718, 1722, 1742, 1746, 1766, 1770, 1790, 1794, 1816, 1820, 1840, 1844, 1868, 1872, 1894, 1898, 1920, 1924, 1946, 1950, 1972, 1976, 1998, 2002, 2024, 2028, 2050, 2054, 2076, 2080, 2090, 2094, 2104, 2108, 2118, 2122, 2138, 2142, 2152, 2156, 2178, 2182, 2203, 2207, 2229, 2233, 2236, 2288, 2609, 2629, 2633, 2643, 2647, 2657, 2661, 2683, 2687, 2709, 2713, 2735, 2739, 2760, 2764, 2785, 2789, 2798, 2802, 2811, 2815, 2839, 2843, 2863, 2867, 2889, 2893, 2899, 2903, 2925, 2929, 2939, 2943, 2965, 2969, 2979, 2983, 3005, 3009, 3017, 3021, 3031, 3035, 3051, 3055, 3065, 3069, 3085, 3089, 3099, 3103, 3113, 3117, 3127, 3131, 3153, 3157, 3179, 3183, 3205, 3209, 3231, 3235, 3257, 3261, 3283, 3287, 3309, 3313, 3335, 3339, 3361, 3365, 3387, 3391, 3412, 3416, 3440, 3444, 3460, 3464, 3486, 3490, 3512, 3516, 3538, 3542, 3564, 3568, 3584, 3588, 3604, 3608, 3630, 3634, 3656, 3660, 3682, 3686, 3708, 3712, 3728, 3732, 3742, 3746, 3768, 3772, 3800, 3804, 3826, 3830, 3852, 3856, 3866, 3870, 3880, 3884, 3906, 3910, 3932, 3936, 3957, 3961, 3977, 3981, 3983
frontend/node_modules/fs-extra/README.md: conflict markers at lines 2
frontend/node_modules/co/History.md: conflict markers at lines 2, 12, 17, 24, 29, 34, 39, 44, 49, 55, 63, 70, 76, 81, 86, 91, 96, 104, 109, 114, 119, 125, 130, 135, 141, 146, 154, 159, 164, 169
frontend/node_modules/tweetnacl/CHANGELOG.md: conflict markers at lines 2
frontend/node_modules/tweetnacl/README.md: conflict markers at lines 2, 17
frontend/node_modules/tweetnacl/AUTHORS.md: conflict markers at lines 2, 12
frontend/node_modules/nan/README.md: conflict markers at lines 2
frontend/node_modules/is-callable/CHANGELOG.md: conflict markers at lines 52, 66, 74, 79, 85, 93, 104, 110, 116, 124, 132, 140, 144, 149, 153, 157
frontend/node_modules/run-async/README.md: conflict markers at lines 2, 9, 16, 76
frontend/node_modules/natural-compare/README.md: conflict markers at lines 17
frontend/node_modules/cpu-features/README.md: conflict markers at lines 3, 9, 16, 22
frontend/node_modules/bl/LICENSE.md: conflict markers at lines 2
frontend/node_modules/mz/HISTORY.md: conflict markers at lines 3, 8, 13, 18, 23, 28, 33, 38, 43, 48, 53, 58, 63
frontend/node_modules/properties-reader/README.md: conflict markers at lines 2, 7, 103, 109, 126
frontend/node_modules/eslint-plugin-jsx-a11y/CHANGELOG.md: conflict markers at lines 178, 195, 225, 230, 285, 289, 312, 320, 368, 372, 409, 413, 439, 444, 450, 459, 464, 469, 481, 485, 494, 499, 504, 509, 523, 538, 542, 551, 557, 562, 567, 576, 584, 590, 595, 600, 605, 610, 615, 620, 629, 634, 639, 645, 651, 656, 661, 667, 672, 681, 686, 691, 696, 701, 721, 726, 731, 737, 742, 747, 752, 757, 762, 768, 773
frontend/node_modules/makeerror/readme.md: conflict markers at lines 2
frontend/node_modules/didyoumean/README.md: conflict markers at lines 2
frontend/node_modules/didyoumean/didYouMean-1.2.1.js: conflict markers at lines 4
frontend/node_modules/thenify-all/History.md: conflict markers at lines 3, 9
frontend/node_modules/agent-base/README.md: conflict markers at lines 2
frontend/node_modules/symbol-tree/README.md: conflict markers at lines 2
frontend/node_modules/jsx-ast-utils/CHANGELOG.md: conflict markers at lines 37, 43, 47, 55, 60, 65, 84, 91, 97, 107, 111, 117, 126, 130, 134, 138, 145, 154, 159, 164, 169, 174, 179, 184, 189, 194, 199, 204, 209, 214, 219, 225, 230
frontend/node_modules/next/dist/compiled/@vercel/og/LICENSE: conflict markers at lines 2
frontend/node_modules/next/dist/compiled/@vercel/og/satori/LICENSE: conflict markers at lines 2
frontend/node_modules/@babel/core/node_modules/semver/README.md: conflict markers at lines 2
frontend/node_modules/@babel/helper-compilation-targets/node_modules/semver/README.md: conflict markers at lines 2
frontend/node_modules/eslint-module-utils/node_modules/debug/CHANGELOG.md: conflict markers at lines 3, 15, 20, 36, 41, 46, 53, 61, 68, 74, 81, 89, 96, 103, 108, 121, 130, 135, 140, 147, 152, 162, 169, 175, 183, 203, 212, 221, 232, 241, 248, 254, 266, 272, 280, 289, 312, 317, 324, 329, 336, 343, 351, 357, 363, 371, 378, 383, 388, 393
frontend/node_modules/@istanbuljs/load-nyc-config/node_modules/argparse/README.md: conflict markers at lines 2, 23, 86, 116, 146, 179, 243, 251
frontend/node_modules/@istanbuljs/load-nyc-config/node_modules/js-yaml/README.md: conflict markers at lines 2
frontend/node_modules/protobufjs/ext/descriptor/README.md: conflict markers at lines 2
frontend/node_modules/protobufjs/ext/debug/README.md: conflict markers at lines 2
frontend/node_modules/eslint-plugin-import/node_modules/semver/README.md: conflict markers at lines 2
frontend/node_modules/eslint-plugin-import/node_modules/debug/CHANGELOG.md: conflict markers at lines 3, 15, 20, 36, 41, 46, 53, 61, 68, 74, 81, 89, 96, 103, 108, 121, 130, 135, 140, 147, 152, 162, 169, 175, 183, 203, 212, 221, 232, 241, 248, 254, 266, 272, 280, 289, 312, 317, 324, 329, 336, 343, 351, 357, 363, 371, 378, 383, 388, 393
frontend/node_modules/eslint-plugin-react/node_modules/semver/README.md: conflict markers at lines 2
frontend/node_modules/playwright-core/lib/server/recorder/contextRecorder.js: conflict markers at lines 114, 116
frontend/node_modules/@fastify/busboy/README.md: conflict markers at lines 20, 37, 43, 49
frontend/node_modules/eslint-import-resolver-node/node_modules/debug/CHANGELOG.md: conflict markers at lines 3, 15, 20, 36, 41, 46, 53, 61, 68, 74, 81, 89, 96, 103, 108, 121, 130, 135, 140, 147, 152, 162, 169, 175, 183, 203, 212, 221, 232, 241, 248, 254, 266, 272, 280, 289, 312, 317, 324, 329, 336, 343, 351, 357, 363, 371, 378, 383, 388, 393
frontend/node_modules/@protobufjs/fetch/README.md: conflict markers at lines 2
frontend/node_modules/@protobufjs/aspromise/README.md: conflict markers at lines 2
frontend/node_modules/@protobufjs/path/README.md: conflict markers at lines 2
frontend/node_modules/@protobufjs/pool/README.md: conflict markers at lines 2
frontend/node_modules/@protobufjs/eventemitter/README.md: conflict markers at lines 2
frontend/node_modules/@protobufjs/base64/README.md: conflict markers at lines 2
frontend/node_modules/@protobufjs/codegen/README.md: conflict markers at lines 2
frontend/node_modules/@protobufjs/utf8/README.md: conflict markers at lines 2
frontend/node_modules/@protobufjs/inquire/README.md: conflict markers at lines 2
frontend/node_modules/@protobufjs/float/README.md: conflict markers at lines 2
frontend/node_modules/playwright/lib/transform/babelBundleImpl.js: conflict markers at lines 30
frontend/node_modules/exit/test/exit_test.js: conflict markers at lines 4
frontend/node_modules/babel-plugin-istanbul/node_modules/semver/README.md: conflict markers at lines 2

```
## Ação
Forneça um plano de correção passo a passo.