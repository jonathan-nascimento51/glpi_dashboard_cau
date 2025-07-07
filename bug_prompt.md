# Identidade
Você é um assistente de depuração para o projeto GLPI Dashboard.

## Instruções
Analise os erros abaixo e sugira correções de código mantendo o estilo do projeto.

## Erros e avisos
### pytest
```
ERROR: usage: pytest [options] [file_or_dir] [file_or_dir] [...]
pytest: error: unrecognized arguments: --cov=./ --cov-report=term-missing --cov-fail-under=70
  inifile: /workspace/glpi_dashboard_cau/pytest.ini
  rootdir: /workspace/glpi_dashboard_cau


```
### flake8
```
Command not found: flake8

```
### merge_conflicts
```
.venv/lib/python3.12/site-packages/propcache-0.3.2.dist-info/METADATA: conflict markers at lines 41, 139, 141
.venv/lib/python3.12/site-packages/plotly/tools.py: conflict markers at lines 86, 94
.venv/lib/python3.12/site-packages/requests_mock-1.12.1.dist-info/METADATA: conflict markers at lines 31, 33, 45, 104, 109, 114
.venv/lib/python3.12/site-packages/psutil-6.1.1.dist-info/METADATA: conflict markers at lines 149, 162, 184, 197, 206, 527, 540
.venv/lib/python3.12/site-packages/opentelemetry_instrumentation_asgi-0.55b1.dist-info/METADATA: conflict markers at lines 31
.venv/lib/python3.12/site-packages/mypy_extensions-1.1.0.dist-info/METADATA: conflict markers at lines 24
.venv/lib/python3.12/site-packages/opentelemetry_instrumentation-0.55b1.dist-info/METADATA: conflict markers at lines 28
.venv/lib/python3.12/site-packages/certifi-2025.6.15.dist-info/METADATA: conflict markers at lines 38
.venv/lib/python3.12/site-packages/opentelemetry_proto-1.34.1.dist-info/METADATA: conflict markers at lines 26
.venv/lib/python3.12/site-packages/identify-2.6.12.dist-info/METADATA: conflict markers at lines 23
.venv/lib/python3.12/site-packages/iniconfig-2.1.0.dist-info/METADATA: conflict markers at lines 29, 46
.venv/lib/python3.12/site-packages/pytest-8.4.1.dist-info/METADATA: conflict markers at lines 116, 121, 130
.venv/lib/python3.12/site-packages/pycodestyle-2.14.0.dist-info/METADATA: conflict markers at lines 28
.venv/lib/python3.12/site-packages/requests_toolbelt-1.0.0.dist-info/METADATA: conflict markers at lines 35, 145
.venv/lib/python3.12/site-packages/multidict-6.6.3.dist-info/METADATA: conflict markers at lines 33, 35
.venv/lib/python3.12/site-packages/tzdata-2025.2.dist-info/METADATA: conflict markers at lines 24
.venv/lib/python3.12/site-packages/cachelib-0.13.0.dist-info/METADATA: conflict markers at lines 26
.venv/lib/python3.12/site-packages/waitress-3.0.2.dist-info/METADATA: conflict markers at lines 44
.venv/lib/python3.12/site-packages/trio-0.30.0.dist-info/METADATA: conflict markers at lines 67
.venv/lib/python3.12/site-packages/sniffio/_impl.py: conflict markers at lines 30, 32, 38
.venv/lib/python3.12/site-packages/opentelemetry_util_http-0.55b1.dist-info/METADATA: conflict markers at lines 23
.venv/lib/python3.12/site-packages/Flask_Caching-2.3.1.dist-info/METADATA: conflict markers at lines 31
.venv/lib/python3.12/site-packages/packaging-24.2.dist-info/METADATA: conflict markers at lines 28
.venv/lib/python3.12/site-packages/zstandard-0.23.0.dist-info/METADATA: conflict markers at lines 26, 28
.venv/lib/python3.12/site-packages/jsonpointer-3.0.0.dist-info/METADATA: conflict markers at lines 32
.venv/lib/python3.12/site-packages/xxhash-3.5.0.dist-info/METADATA: conflict markers at lines 28
.venv/lib/python3.12/site-packages/aiohttp-3.12.13.dist-info/METADATA: conflict markers at lines 48, 50, 89, 98, 173, 185, 198, 209, 226, 232, 240, 246
.venv/lib/python3.12/site-packages/backoff-2.2.1.dist-info/METADATA: conflict markers at lines 34, 61
.venv/lib/python3.12/site-packages/pytest_asyncio-1.0.0.dist-info/METADATA: conflict markers at lines 38
.venv/lib/python3.12/site-packages/importlib_metadata-8.7.0.dist-info/METADATA: conflict markers at lines 75, 111, 120, 128
.venv/lib/python3.12/site-packages/multiprocess-0.70.18.dist-info/METADATA: conflict markers at lines 58, 68, 83, 93, 103, 113, 123, 185, 204
.venv/lib/python3.12/site-packages/pip-25.1.1.dist-info/METADATA: conflict markers at lines 32
.venv/lib/python3.12/site-packages/setuptools-80.9.0.dist-info/METADATA: conflict markers at lines 127, 135
.venv/lib/python3.12/site-packages/opentelemetry_api-1.34.1.dist-info/METADATA: conflict markers at lines 28
.venv/lib/python3.12/site-packages/opentelemetry_exporter_otlp_proto_http-1.34.1.dist-info/METADATA: conflict markers at lines 33
.venv/lib/python3.12/site-packages/tzlocal-5.3.1.dist-info/METADATA: conflict markers at lines 34
.venv/lib/python3.12/site-packages/requests_toolbelt/__init__.py: conflict markers at lines 4
.venv/lib/python3.12/site-packages/requests_toolbelt/streaming_iterator.py: conflict markers at lines 5
.venv/lib/python3.12/site-packages/retrying-1.4.0.dist-info/METADATA: conflict markers at lines 40
.venv/lib/python3.12/site-packages/SQLAlchemy-2.0.30.dist-info/METADATA: conflict markers at lines 86
.venv/lib/python3.12/site-packages/multiprocess/__info__.py: conflict markers at lines 13, 23, 38, 48, 58, 68, 78, 140, 159
.venv/lib/python3.12/site-packages/pkg_resources/api_tests.txt: conflict markers at lines 2
.venv/lib/python3.12/site-packages/greenlet-3.2.3.dist-info/METADATA: conflict markers at lines 88, 102
.venv/lib/python3.12/site-packages/numpy/exceptions.py: conflict markers at lines 3
.venv/lib/python3.12/site-packages/opentelemetry_sdk-1.34.1.dist-info/METADATA: conflict markers at lines 29
.venv/lib/python3.12/site-packages/dill-0.4.0.dist-info/METADATA: conflict markers at lines 46, 78, 107, 117, 127, 147, 162, 248, 266
.venv/lib/python3.12/site-packages/platformdirs-4.3.8.dist-info/METADATA: conflict markers at lines 45, 81, 106, 257, 293, 332
.venv/lib/python3.12/site-packages/distlib-0.3.9.dist-info/LICENSE.txt: conflict markers at lines 2, 91
.venv/lib/python3.12/site-packages/opentelemetry_instrumentation_logging-0.55b1.dist-info/METADATA: conflict markers at lines 27
.venv/lib/python3.12/site-packages/pytz-2025.2.dist-info/METADATA: conflict markers at lines 43
.venv/lib/python3.12/site-packages/flake8-7.3.0.dist-info/METADATA: conflict markers at lines 42, 44, 70, 78, 85, 115
.venv/lib/python3.12/site-packages/PyJWT-2.9.0.dist-info/AUTHORS.rst: conflict markers at lines 2
.venv/lib/python3.12/site-packages/opentelemetry_exporter_otlp_proto_common-1.34.1.dist-info/METADATA: conflict markers at lines 27
.venv/lib/python3.12/site-packages/pluggy-1.6.0.dist-info/METADATA: conflict markers at lines 37, 39, 48
.venv/lib/python3.12/site-packages/cryptography-45.0.5.dist-info/METADATA: conflict markers at lines 72
.venv/lib/python3.12/site-packages/sniffio-1.3.1.dist-info/METADATA: conflict markers at lines 53, 55
.venv/lib/python3.12/site-packages/jsonpatch-1.33.dist-info/METADATA: conflict markers at lines 38
.venv/lib/python3.12/site-packages/pandas/__init__.py: conflict markers at lines 211
.venv/lib/python3.12/site-packages/pyopenssl-25.1.0.dist-info/METADATA: conflict markers at lines 53, 55, 81, 98
.venv/lib/python3.12/site-packages/outcome-1.3.0.post0.dist-info/METADATA: conflict markers at lines 56
.venv/lib/python3.12/site-packages/idna-3.10.dist-info/METADATA: conflict markers at lines 39
.venv/lib/python3.12/site-packages/pathspec-0.12.1.dist-info/METADATA: conflict markers at lines 29, 196
.venv/lib/python3.12/site-packages/pathspec-0.12.1.dist-info/LICENSE: conflict markers at lines 2
.venv/lib/python3.12/site-packages/urllib3-1.26.20.dist-info/METADATA: conflict markers at lines 158
.venv/lib/python3.12/site-packages/mccabe-0.7.0.dist-info/METADATA: conflict markers at lines 30
.venv/lib/python3.12/site-packages/gql/cli.py: conflict markers at lines 24
.venv/lib/python3.12/site-packages/yarl-1.20.1.dist-info/METADATA: conflict markers at lines 254, 256, 1593, 1677, 1747, 1757, 1766, 1799, 1805, 1814, 1843, 1852, 1860, 1873, 1888, 1898, 1933, 1955, 1974, 2019, 2032, 2037, 2061, 2075, 2080, 2085, 2090, 2095, 2100, 2105, 2112, 2117, 2122, 2140, 2145, 2150, 2156, 2161, 2166, 2172, 2179, 2190, 2197, 2204, 2209, 2215, 2223, 2231, 2237, 2245, 2251, 2257, 2263, 2269, 2275, 2281, 2297, 2303, 2313, 2318, 2323, 2329, 2334, 2339, 2344, 2350, 2355, 2360, 2365, 2370, 2375, 2380, 2385, 2390, 2397, 2402, 2409, 2414, 2419, 2425
.venv/lib/python3.12/site-packages/aiosqlite-0.21.0.dist-info/METADATA: conflict markers at lines 32
.venv/lib/python3.12/site-packages/pytest_mock-3.14.1.dist-info/METADATA: conflict markers at lines 38, 40, 96, 101
.venv/lib/python3.12/site-packages/sortedcontainers/sorteddict.py: conflict markers at lines 2
.venv/lib/python3.12/site-packages/sortedcontainers/sortedlist.py: conflict markers at lines 2
.venv/lib/python3.12/site-packages/sortedcontainers/sortedset.py: conflict markers at lines 2
.venv/lib/python3.12/site-packages/dill/__info__.py: conflict markers at lines 13, 45, 74, 84, 94, 114, 129, 215, 233
.venv/lib/python3.12/site-packages/sortedcontainers-2.4.0.dist-info/METADATA: conflict markers at lines 28
.venv/lib/python3.12/site-packages/python_dateutil-2.9.0.post0.dist-info/METADATA: conflict markers at lines 38, 86, 93, 106, 129, 161, 183, 185, 187, 193, 198
.venv/lib/python3.12/site-packages/asgiref-3.9.0.dist-info/METADATA: conflict markers at lines 36
.venv/lib/python3.12/site-packages/opentelemetry_semantic_conventions-0.55b1.dist-info/METADATA: conflict markers at lines 27
.venv/lib/python3.12/site-packages/_pytest/_argcomplete.py: conflict markers at lines 22, 34
.venv/lib/python3.12/site-packages/_pytest/pytester.py: conflict markers at lines 562, 574
.venv/lib/python3.12/site-packages/_pytest/hookspec.py: conflict markers at lines 67, 90, 131, 150, 182, 199, 218, 265, 287, 299, 339, 369, 405, 422, 437, 451, 474, 491, 534, 560, 578, 593, 616, 647, 688, 705, 725, 744, 760, 784, 804, 818, 837, 855, 888, 909, 929, 945, 957, 984, 1018, 1060, 1105, 1138, 1159, 1197, 1227, 1252, 1266, 1297, 1314, 1330
.venv/lib/python3.12/site-packages/opentelemetry_instrumentation_fastapi-0.55b1.dist-info/METADATA: conflict markers at lines 31
.venv/lib/python3.12/site-packages/purgatory-3.0.1.dist-info/METADATA: conflict markers at lines 31
.venv/lib/python3.12/site-packages/pytest_cov-6.2.1.dist-info/METADATA: conflict markers at lines 56, 58, 116, 164, 174, 184, 197, 203, 221
.venv/lib/python3.12/site-packages/frozenlist-1.7.0.dist-info/METADATA: conflict markers at lines 39, 148, 150, 322, 378, 485, 518, 528, 540, 550, 570, 589, 602, 620
.venv/lib/python3.12/site-packages/pandas-2.3.0.dist-info/METADATA: conflict markers at lines 612, 670
.venv/lib/python3.12/site-packages/pandas-2.3.0.dist-info/LICENSE: conflict markers at lines 607, 665
.venv/lib/python3.12/site-packages/selenium-4.2.0.dist-info/METADATA: conflict markers at lines 23, 25, 28, 49, 54, 67, 87, 100, 124, 147, 162
.venv/lib/python3.12/site-packages/aiosignal-1.4.0.dist-info/METADATA: conflict markers at lines 32, 34, 61, 93, 98, 103
.venv/lib/python3.12/site-packages/mypy-1.16.1.dist-info/METADATA: conflict markers at lines 45
.venv/lib/python3.12/site-packages/googleapis_common_protos-1.70.0.dist-info/METADATA: conflict markers at lines 30
.venv/lib/python3.12/site-packages/pybreaker-1.4.0.dist-info/METADATA: conflict markers at lines 28
.venv/lib/python3.12/site-packages/coverage-7.9.2.dist-info/METADATA: conflict markers at lines 53, 55
.venv/lib/python3.12/site-packages/pyflakes-3.4.0.dist-info/METADATA: conflict markers at lines 23, 25
.venv/lib/python3.12/site-packages/nodeenv-1.9.1.dist-info/METADATA: conflict markers at lines 29, 305, 311
.venv/lib/python3.12/site-packages/PySocks-1.7.1.dist-info/METADATA: conflict markers at lines 21, 30, 39
.venv/lib/python3.12/site-packages/zipp-3.23.0.dist-info/METADATA: conflict markers at lines 69, 100
.venv/lib/python3.12/site-packages/lxml-6.0.0.dist-info/METADATA: conflict markers at lines 79
.venv/lib/python3.12/site-packages/coverage/plugin.py: conflict markers at lines 63, 77, 92
.venv/lib/python3.12/site-packages/asyncpg-0.30.0.dist-info/METADATA: conflict markers at lines 46
.venv/lib/python3.12/site-packages/asyncpg-0.30.0.dist-info/AUTHORS: conflict markers at lines 2
.venv/lib/python3.12/site-packages/wsproto-1.2.0.dist-info/METADATA: conflict markers at lines 25, 27, 119, 151, 156, 168, 174
.venv/lib/python3.12/site-packages/aiohappyeyeballs-2.6.1.dist-info/LICENSE: conflict markers at lines 2, 60
.venv/lib/python3.12/site-packages/blib2to3/LICENSE: conflict markers at lines 2, 60
.venv/lib/python3.12/site-packages/plotly/figure_factory/_ternary_contour.py: conflict markers at lines 22, 193, 394, 566
.venv/lib/python3.12/site-packages/plotly/matplotlylib/__init__.py: conflict markers at lines 5
.venv/lib/python3.12/site-packages/plotly/__pycache__/tools.cpython-312.pyc: conflict markers at lines 43, 51
.venv/lib/python3.12/site-packages/plotly/figure_factory/__pycache__/_ternary_contour.cpython-312.pyc: conflict markers at lines 17, 129, 282, 377
.venv/lib/python3.12/site-packages/plotly/matplotlylib/mplexporter/exporter.py: conflict markers at lines 3
.venv/lib/python3.12/site-packages/plotly/matplotlylib/mplexporter/utils.py: conflict markers at lines 3
.venv/lib/python3.12/site-packages/plotly/matplotlylib/__pycache__/__init__.cpython-312.pyc: conflict markers at lines 5
.venv/lib/python3.12/site-packages/plotly/matplotlylib/mplexporter/renderers/__init__.py: conflict markers at lines 5
.venv/lib/python3.12/site-packages/plotly/matplotlylib/mplexporter/__pycache__/utils.cpython-312.pyc: conflict markers at lines 11
.venv/lib/python3.12/site-packages/plotly/matplotlylib/mplexporter/__pycache__/exporter.cpython-312.pyc: conflict markers at lines 6
.venv/lib/python3.12/site-packages/plotly/matplotlylib/mplexporter/renderers/__pycache__/__init__.cpython-312.pyc: conflict markers at lines 7
.venv/lib/python3.12/site-packages/setuptools/tests/test_windows_wrappers.py: conflict markers at lines 3
.venv/lib/python3.12/site-packages/setuptools/_vendor/more_itertools-10.3.0.dist-info/METADATA: conflict markers at lines 25, 27, 203, 244, 254, 263
.venv/lib/python3.12/site-packages/setuptools/_vendor/jaraco.collections-5.1.0.dist-info/METADATA: conflict markers at lines 79
.venv/lib/python3.12/site-packages/setuptools/_vendor/zipp-3.19.2.dist-info/METADATA: conflict markers at lines 65, 96
.venv/lib/python3.12/site-packages/setuptools/_vendor/packaging-24.2.dist-info/METADATA: conflict markers at lines 28
.venv/lib/python3.12/site-packages/setuptools/_vendor/jaraco.functools-4.0.1.dist-info/METADATA: conflict markers at lines 58
.venv/lib/python3.12/site-packages/setuptools/_vendor/platformdirs-4.2.2.dist-info/METADATA: conflict markers at lines 44, 74, 99, 236, 266, 301
.venv/lib/python3.12/site-packages/setuptools/_vendor/importlib_metadata-8.0.0.dist-info/METADATA: conflict markers at lines 70, 106, 115, 123
.venv/lib/python3.12/site-packages/setuptools/_vendor/jaraco.text-3.12.1.dist-info/METADATA: conflict markers at lines 67, 79, 89
.venv/lib/python3.12/site-packages/setuptools/_vendor/jaraco.context-5.3.0.dist-info/METADATA: conflict markers at lines 56, 69
.venv/lib/python3.12/site-packages/setuptools/_vendor/typing_extensions-4.12.2.dist-info/LICENSE: conflict markers at lines 2, 60
.venv/lib/python3.12/site-packages/setuptools/_vendor/inflect-7.3.1.dist-info/METADATA: conflict markers at lines 68, 289, 323, 572, 585
.venv/lib/python3.12/site-packages/setuptools/tests/__pycache__/test_windows_wrappers.cpython-312.pyc: conflict markers at lines 8
.venv/lib/python3.12/site-packages/setuptools/config/_validate_pyproject/NOTICE: conflict markers at lines 40, 75
.venv/lib/python3.12/site-packages/strawberry/ext/dataclasses/LICENSE: conflict markers at lines 2, 60
.venv/lib/python3.12/site-packages/playwright/driver/package/ThirdPartyNotices.txt: conflict markers at lines 53, 55, 199, 203, 225, 229, 251, 255, 275, 279, 301, 305, 331, 335, 358, 362, 381, 385, 405, 409, 429, 433, 443, 447, 477, 481, 505, 509, 531, 535, 545, 549, 565, 569, 571, 707, 711, 731, 735, 745, 749, 759, 763, 789, 793, 834, 838, 860, 864, 880, 884, 906, 910, 932, 936, 952, 956, 966, 970, 994, 998, 1019, 1023, 1046, 1050, 1071, 1075, 1097, 1101, 1123, 1127, 1144, 1148, 1169, 1173, 1175, 1326, 1330, 1351, 1355, 1380, 1384, 1400, 1404, 1425, 1429, 1443, 1447, 1469, 1473, 1495, 1499, 1501
.venv/lib/python3.12/site-packages/playwright/driver/package/lib/server/recorder/contextRecorder.js: conflict markers at lines 114, 116
.venv/lib/python3.12/site-packages/pydantic/_internal/_typing_extra.py: conflict markers at lines 605
.venv/lib/python3.12/site-packages/pydantic/_internal/__pycache__/_typing_extra.cpython-312.pyc: conflict markers at lines 282
.venv/lib/python3.12/site-packages/sniffio/__pycache__/_impl.cpython-312.pyc: conflict markers at lines 16, 18, 24
.venv/lib/python3.12/site-packages/graphql/utilities/value_from_ast_untyped.py: conflict markers at lines 30, 32, 39
.venv/lib/python3.12/site-packages/graphql/utilities/value_from_ast.py: conflict markers at lines 39, 41, 49
.venv/lib/python3.12/site-packages/graphql/utilities/ast_from_value.py: conflict markers at lines 48, 50, 58
.venv/lib/python3.12/site-packages/graphql/utilities/__pycache__/value_from_ast.cpython-312.pyc: conflict markers at lines 44, 46, 54
.venv/lib/python3.12/site-packages/graphql/utilities/__pycache__/ast_from_value.cpython-312.pyc: conflict markers at lines 27, 29, 37
.venv/lib/python3.12/site-packages/graphql/utilities/__pycache__/value_from_ast_untyped.cpython-312.pyc: conflict markers at lines 32, 34, 41
.venv/lib/python3.12/site-packages/werkzeug/middleware/dispatcher.py: conflict markers at lines 3
.venv/lib/python3.12/site-packages/werkzeug/middleware/proxy_fix.py: conflict markers at lines 3
.venv/lib/python3.12/site-packages/werkzeug/middleware/shared_data.py: conflict markers at lines 3
.venv/lib/python3.12/site-packages/werkzeug/middleware/profiler.py: conflict markers at lines 3
.venv/lib/python3.12/site-packages/werkzeug/middleware/http_proxy.py: conflict markers at lines 3
.venv/lib/python3.12/site-packages/werkzeug/middleware/lint.py: conflict markers at lines 3
.venv/lib/python3.12/site-packages/werkzeug/middleware/__pycache__/http_proxy.cpython-312.pyc: conflict markers at lines 9
.venv/lib/python3.12/site-packages/werkzeug/middleware/__pycache__/lint.cpython-312.pyc: conflict markers at lines 10
.venv/lib/python3.12/site-packages/werkzeug/middleware/__pycache__/profiler.cpython-312.pyc: conflict markers at lines 9
.venv/lib/python3.12/site-packages/werkzeug/middleware/__pycache__/proxy_fix.cpython-312.pyc: conflict markers at lines 8
.venv/lib/python3.12/site-packages/werkzeug/middleware/__pycache__/dispatcher.cpython-312.pyc: conflict markers at lines 8
.venv/lib/python3.12/site-packages/werkzeug/middleware/__pycache__/shared_data.cpython-312.pyc: conflict markers at lines 14
.venv/lib/python3.12/site-packages/identify/vendor/licenses.py: conflict markers at lines 1407, 1459, 1780, 1807, 1859, 2212, 5383, 5412, 5468, 5577, 5600, 5672, 5819
.venv/lib/python3.12/site-packages/identify/vendor/__pycache__/licenses.cpython-312.pyc: conflict markers at lines 1360, 1412, 1733, 1755, 1807, 2160, 5271, 5300, 5356, 5465, 5488, 5560, 5697
.venv/lib/python3.12/site-packages/opentelemetry/sdk/metrics/_internal/aggregation.py: conflict markers at lines 1220, 1222, 1229
.venv/lib/python3.12/site-packages/opentelemetry/sdk/metrics/_internal/__pycache__/aggregation.cpython-312.pyc: conflict markers at lines 416, 418, 425
.venv/lib/python3.12/site-packages/requests_toolbelt/adapters/ssl.py: conflict markers at lines 5
.venv/lib/python3.12/site-packages/requests_toolbelt/adapters/host_header_ssl.py: conflict markers at lines 4
.venv/lib/python3.12/site-packages/requests_toolbelt/adapters/source.py: conflict markers at lines 4
.venv/lib/python3.12/site-packages/requests_toolbelt/adapters/__init__.py: conflict markers at lines 4
.venv/lib/python3.12/site-packages/requests_toolbelt/multipart/decoder.py: conflict markers at lines 5
.venv/lib/python3.12/site-packages/requests_toolbelt/multipart/encoder.py: conflict markers at lines 5
.venv/lib/python3.12/site-packages/requests_toolbelt/multipart/__init__.py: conflict markers at lines 3
.venv/lib/python3.12/site-packages/requests_toolbelt/auth/handler.py: conflict markers at lines 5
.venv/lib/python3.12/site-packages/requests_toolbelt/__pycache__/streaming_iterator.cpython-312.pyc: conflict markers at lines 7
.venv/lib/python3.12/site-packages/requests_toolbelt/__pycache__/__init__.cpython-312.pyc: conflict markers at lines 11
.venv/lib/python3.12/site-packages/requests_toolbelt/adapters/__pycache__/host_header_ssl.cpython-312.pyc: conflict markers at lines 5
.venv/lib/python3.12/site-packages/requests_toolbelt/adapters/__pycache__/ssl.cpython-312.pyc: conflict markers at lines 6
.venv/lib/python3.12/site-packages/requests_toolbelt/adapters/__pycache__/source.cpython-312.pyc: conflict markers at lines 6
.venv/lib/python3.12/site-packages/requests_toolbelt/adapters/__pycache__/__init__.cpython-312.pyc: conflict markers at lines 5
.venv/lib/python3.12/site-packages/requests_toolbelt/multipart/__pycache__/decoder.cpython-312.pyc: conflict markers at lines 11
.venv/lib/python3.12/site-packages/requests_toolbelt/multipart/__pycache__/encoder.cpython-312.pyc: conflict markers at lines 10
.venv/lib/python3.12/site-packages/requests_toolbelt/multipart/__pycache__/__init__.cpython-312.pyc: conflict markers at lines 7
.venv/lib/python3.12/site-packages/requests_toolbelt/auth/__pycache__/handler.cpython-312.pyc: conflict markers at lines 6
.venv/lib/python3.12/site-packages/multiprocess/__pycache__/__info__.cpython-312.pyc: conflict markers at lines 9, 19, 34, 44, 54, 64, 74, 136, 155
.venv/lib/python3.12/site-packages/sqlalchemy/ext/automap.py: conflict markers at lines 33, 92, 136, 239, 299, 368, 621, 674
.venv/lib/python3.12/site-packages/sqlalchemy/ext/indexable.py: conflict markers at lines 26, 151, 176
.venv/lib/python3.12/site-packages/sqlalchemy/ext/compiler.py: conflict markers at lines 12, 43, 72, 141, 166, 184, 263, 343
.venv/lib/python3.12/site-packages/sqlalchemy/ext/mutable.py: conflict markers at lines 14, 231
.venv/lib/python3.12/site-packages/sqlalchemy/ext/__pycache__/compiler.cpython-312.pyc: conflict markers at lines 6, 37, 66, 135, 160, 178, 257, 337
.venv/lib/python3.12/site-packages/sqlalchemy/ext/__pycache__/mutable.cpython-312.pyc: conflict markers at lines 17, 234
.venv/lib/python3.12/site-packages/sqlalchemy/ext/__pycache__/automap.cpython-312.pyc: conflict markers at lines 36, 95, 139, 242, 302, 371, 624, 677
.venv/lib/python3.12/site-packages/sqlalchemy/ext/__pycache__/indexable.cpython-312.pyc: conflict markers at lines 20, 145, 170
.venv/lib/python3.12/site-packages/numpy/ma/API_CHANGES.txt: conflict markers at lines 3, 5, 117, 119
.venv/lib/python3.12/site-packages/numpy/ma/core.py: conflict markers at lines 267, 269, 276
.venv/lib/python3.12/site-packages/numpy/ma/__init__.py: conflict markers at lines 2, 4
.venv/lib/python3.12/site-packages/numpy/ma/README.rst: conflict markers at lines 1, 3
.venv/lib/python3.12/site-packages/numpy/polynomial/chebyshev.py: conflict markers at lines 2, 4
.venv/lib/python3.12/site-packages/numpy/polynomial/hermite_e.py: conflict markers at lines 2, 4
.venv/lib/python3.12/site-packages/numpy/polynomial/laguerre.py: conflict markers at lines 2, 4
.venv/lib/python3.12/site-packages/numpy/polynomial/hermite.py: conflict markers at lines 2, 4
.venv/lib/python3.12/site-packages/numpy/polynomial/legendre.py: conflict markers at lines 2, 4
.venv/lib/python3.12/site-packages/numpy/polynomial/polynomial.py: conflict markers at lines 2, 4
.venv/lib/python3.12/site-packages/numpy/polynomial/__init__.py: conflict markers at lines 18, 20, 27, 57
.venv/lib/python3.12/site-packages/numpy/_core/fromnumeric.py: conflict markers at lines 815, 817, 819, 1020, 1022, 1027
.venv/lib/python3.12/site-packages/numpy/typing/__init__.py: conflict markers at lines 2, 4
.venv/lib/python3.12/site-packages/numpy/lib/_function_base_impl.py: conflict markers at lines 4428, 4430, 4437, 5740, 5742, 5747
.venv/lib/python3.12/site-packages/numpy/lib/_format_impl.py: conflict markers at lines 5
.venv/lib/python3.12/site-packages/numpy/lib/_histograms_impl.py: conflict markers at lines 361, 370
.venv/lib/python3.12/site-packages/numpy/doc/ufuncs.py: conflict markers at lines 2, 4, 23, 58, 104, 123
.venv/lib/python3.12/site-packages/numpy/__pycache__/exceptions.cpython-312.pyc: conflict markers at lines 9
.venv/lib/python3.12/site-packages/numpy/fft/__init__.py: conflict markers at lines 3
.venv/lib/python3.12/site-packages/numpy/linalg/__init__.py: conflict markers at lines 3
.venv/lib/python3.12/site-packages/numpy/f2py/crackfortran.py: conflict markers at lines 13, 101
.venv/lib/python3.12/site-packages/numpy/random/__init__.py: conflict markers at lines 2, 4, 8, 13, 15, 23, 25, 29, 39, 47, 49, 62, 64, 95, 97, 104, 106, 115, 117, 122
.venv/lib/python3.12/site-packages/numpy/ctypeslib/_ctypeslib.py: conflict markers at lines 2, 4
.venv/lib/python3.12/site-packages/numpy/ma/__pycache__/__init__.cpython-312.pyc: conflict markers at lines 6, 8
.venv/lib/python3.12/site-packages/numpy/ma/__pycache__/core.cpython-312.pyc: conflict markers at lines 113, 115, 122
.venv/lib/python3.12/site-packages/numpy/polynomial/__pycache__/polynomial.cpython-312.pyc: conflict markers at lines 10, 12
.venv/lib/python3.12/site-packages/numpy/polynomial/__pycache__/chebyshev.cpython-312.pyc: conflict markers at lines 9, 11
.venv/lib/python3.12/site-packages/numpy/polynomial/__pycache__/laguerre.cpython-312.pyc: conflict markers at lines 9, 11
.venv/lib/python3.12/site-packages/numpy/polynomial/__pycache__/legendre.cpython-312.pyc: conflict markers at lines 9, 11
.venv/lib/python3.12/site-packages/numpy/polynomial/__pycache__/__init__.cpython-312.pyc: conflict markers at lines 25, 27, 34, 64
.venv/lib/python3.12/site-packages/numpy/polynomial/__pycache__/hermite_e.cpython-312.pyc: conflict markers at lines 9, 11
.venv/lib/python3.12/site-packages/numpy/polynomial/__pycache__/hermite.cpython-312.pyc: conflict markers at lines 9, 11
.venv/lib/python3.12/site-packages/numpy/_core/__pycache__/fromnumeric.cpython-312.pyc: conflict markers at lines 656, 658, 660, 834, 836, 841
.venv/lib/python3.12/site-packages/numpy/typing/__pycache__/__init__.cpython-312.pyc: conflict markers at lines 10, 12
.venv/lib/python3.12/site-packages/numpy/lib/__pycache__/_format_impl.cpython-312.pyc: conflict markers at lines 12
.venv/lib/python3.12/site-packages/numpy/lib/__pycache__/_histograms_impl.cpython-312.pyc: conflict markers at lines 260, 269
.venv/lib/python3.12/site-packages/numpy/lib/__pycache__/_function_base_impl.cpython-312.pyc: conflict markers at lines 3258, 3260, 3267, 4083, 4085, 4090
.venv/lib/python3.12/site-packages/numpy/doc/__pycache__/ufuncs.cpython-312.pyc: conflict markers at lines 4, 6, 25, 60, 106, 125
.venv/lib/python3.12/site-packages/numpy/fft/__pycache__/__init__.cpython-312.pyc: conflict markers at lines 10
.venv/lib/python3.12/site-packages/numpy/linalg/__pycache__/__init__.cpython-312.pyc: conflict markers at lines 5
.venv/lib/python3.12/site-packages/numpy/f2py/__pycache__/rules.cpython-312.pyc: conflict markers at lines 230
.venv/lib/python3.12/site-packages/numpy/f2py/__pycache__/crackfortran.cpython-312.pyc: conflict markers at lines 22, 110
.venv/lib/python3.12/site-packages/numpy/random/__pycache__/__init__.cpython-312.pyc: conflict markers at lines 11, 13, 17, 22, 24, 32, 34, 38, 48, 56, 58, 71, 73, 104, 106, 113, 115, 124, 126, 131
.venv/lib/python3.12/site-packages/numpy/ctypeslib/__pycache__/_ctypeslib.cpython-312.pyc: conflict markers at lines 20, 22
.venv/lib/python3.12/site-packages/langchain_core/runnables/base.py: conflict markers at lines 115, 138, 175, 215
.venv/lib/python3.12/site-packages/langchain_core/runnables/__pycache__/base.cpython-312.pyc: conflict markers at lines 27, 50, 87, 127
.venv/lib/python3.12/site-packages/pact/bin/pact-plugin-cli: conflict markers at lines 64459, 64462
.venv/lib/python3.12/site-packages/pact/lib/ruby/lib/ca-bundle.crt: conflict markers at lines 22, 43, 65, 89, 110, 136, 160, 191, 226, 247, 271, 295, 319, 341, 363, 385, 416, 447, 469, 491, 515, 538, 555, 577, 599, 630, 650, 674, 694, 715, 739, 760, 793, 825, 847, 870, 893, 913, 933, 962, 977, 999, 1020, 1071, 1095, 1126, 1156, 1186, 1208, 1232, 1257, 1287, 1328, 1357, 1386, 1420, 1442, 1463, 1493, 1523, 1553, 1575, 1591, 1613, 1629, 1660, 1692, 1724, 1741, 1755, 1770, 1800, 1830, 1860, 1885, 1904, 1934, 1956, 1977, 2009, 2042, 2060, 2090, 2120, 2140, 2169, 2182, 2196, 2221, 2251, 2275, 2308, 2332, 2364, 2381, 2413, 2430, 2460, 2476, 2506, 2536, 2551, 2566, 2595, 2625, 2659, 2681, 2697, 2718, 2733, 2765, 2799, 2815, 2846, 2862, 2891, 2923, 2939, 2956, 2987, 3003, 3033, 3048, 3078, 3110, 3126
.venv/lib/python3.12/site-packages/pact/lib/ruby/lib/ruby/site_ruby/3.2.0/rubygems/commands/help_command.rb: conflict markers at lines 84, 148, 162, 177, 196
.venv/lib/python3.12/site-packages/pact/lib/ruby/lib/ruby/site_ruby/3.2.0/rubygems/commands/install_command.rb: conflict markers at lines 65, 81, 123
.venv/lib/python3.12/site-packages/pact/lib/ruby/lib/ruby/site_ruby/3.2.0/bundler/man/bundle-show.1.ronn: conflict markers at lines 2
.venv/lib/python3.12/site-packages/pact/lib/ruby/lib/ruby/site_ruby/3.2.0/bundler/man/bundle-lock.1.ronn: conflict markers at lines 2
.venv/lib/python3.12/site-packages/pact/lib/ruby/lib/ruby/site_ruby/3.2.0/bundler/man/bundle-remove.1.ronn: conflict markers at lines 2
.venv/lib/python3.12/site-packages/pact/lib/ruby/lib/ruby/site_ruby/3.2.0/bundler/man/bundle-viz.1.ronn: conflict markers at lines 2
.venv/lib/python3.12/site-packages/pact/lib/ruby/lib/ruby/site_ruby/3.2.0/bundler/man/bundle-config.1.ronn: conflict markers at lines 2
.venv/lib/python3.12/site-packages/pact/lib/ruby/lib/ruby/site_ruby/3.2.0/bundler/man/bundle-open.1.ronn: conflict markers at lines 2
.venv/lib/python3.12/site-packages/pact/lib/ruby/lib/ruby/site_ruby/3.2.0/bundler/man/bundle-doctor.1.ronn: conflict markers at lines 2
.venv/lib/python3.12/site-packages/pact/lib/ruby/lib/ruby/site_ruby/3.2.0/bundler/man/bundle-gem.1.ronn: conflict markers at lines 2
.venv/lib/python3.12/site-packages/pact/lib/ruby/lib/ruby/site_ruby/3.2.0/bundler/man/bundle-init.1.ronn: conflict markers at lines 2
.venv/lib/python3.12/site-packages/pact/lib/ruby/lib/ruby/site_ruby/3.2.0/bundler/man/bundle-info.1.ronn: conflict markers at lines 2
.venv/lib/python3.12/site-packages/pact/lib/ruby/lib/ruby/site_ruby/3.2.0/bundler/man/bundle-inject.1.ronn: conflict markers at lines 2
.venv/lib/python3.12/site-packages/pact/lib/ruby/lib/ruby/site_ruby/3.2.0/bundler/man/bundle-exec.1.ronn: conflict markers at lines 2
.venv/lib/python3.12/site-packages/pact/lib/ruby/lib/ruby/site_ruby/3.2.0/bundler/man/bundle-cache.1.ronn: conflict markers at lines 2
.venv/lib/python3.12/site-packages/pact/lib/ruby/lib/ruby/site_ruby/3.2.0/bundler/man/bundle-list.1.ronn: conflict markers at lines 2
.venv/lib/python3.12/site-packages/pact/lib/ruby/lib/ruby/site_ruby/3.2.0/bundler/man/gemfile.5.ronn: conflict markers at lines 2
.venv/lib/python3.12/site-packages/pact/lib/ruby/lib/ruby/site_ruby/3.2.0/bundler/man/bundle-platform.1.ronn: conflict markers at lines 2
.venv/lib/python3.12/site-packages/pact/lib/ruby/lib/ruby/site_ruby/3.2.0/bundler/man/bundle-update.1.ronn: conflict markers at lines 2
.venv/lib/python3.12/site-packages/pact/lib/ruby/lib/ruby/site_ruby/3.2.0/bundler/man/bundle-clean.1.ronn: conflict markers at lines 2
.venv/lib/python3.12/site-packages/pact/lib/ruby/lib/ruby/site_ruby/3.2.0/bundler/man/bundle-pristine.1.ronn: conflict markers at lines 2
.venv/lib/python3.12/site-packages/pact/lib/ruby/lib/ruby/site_ruby/3.2.0/bundler/man/bundle-outdated.1.ronn: conflict markers at lines 2
.venv/lib/python3.12/site-packages/pact/lib/ruby/lib/ruby/site_ruby/3.2.0/bundler/man/bundle-add.1.ronn: conflict markers at lines 2
.venv/lib/python3.12/site-packages/pact/lib/ruby/lib/ruby/site_ruby/3.2.0/bundler/man/bundle-binstubs.1.ronn: conflict markers at lines 2
.venv/lib/python3.12/site-packages/pact/lib/ruby/lib/ruby/site_ruby/3.2.0/bundler/man/bundle.1.ronn: conflict markers at lines 2
.venv/lib/python3.12/site-packages/pact/lib/ruby/lib/ruby/site_ruby/3.2.0/bundler/man/bundle-install.1.ronn: conflict markers at lines 2
.venv/lib/python3.12/site-packages/pact/lib/ruby/lib/ruby/site_ruby/3.2.0/bundler/man/bundle-check.1.ronn: conflict markers at lines 2
.venv/lib/python3.12/site-packages/pact/lib/ruby/lib/ruby/gems/3.2.0/gems/bundler-2.5.3/lib/bundler/man/bundle-show.1.ronn: conflict markers at lines 2
.venv/lib/python3.12/site-packages/pact/lib/ruby/lib/ruby/gems/3.2.0/gems/bundler-2.5.3/lib/bundler/man/bundle-lock.1.ronn: conflict markers at lines 2
.venv/lib/python3.12/site-packages/pact/lib/ruby/lib/ruby/gems/3.2.0/gems/bundler-2.5.3/lib/bundler/man/bundle-remove.1.ronn: conflict markers at lines 2
.venv/lib/python3.12/site-packages/pact/lib/ruby/lib/ruby/gems/3.2.0/gems/bundler-2.5.3/lib/bundler/man/bundle-viz.1.ronn: conflict markers at lines 2
.venv/lib/python3.12/site-packages/pact/lib/ruby/lib/ruby/gems/3.2.0/gems/bundler-2.5.3/lib/bundler/man/bundle-config.1.ronn: conflict markers at lines 2
.venv/lib/python3.12/site-packages/pact/lib/ruby/lib/ruby/gems/3.2.0/gems/bundler-2.5.3/lib/bundler/man/bundle-open.1.ronn: conflict markers at lines 2
.venv/lib/python3.12/site-packages/pact/lib/ruby/lib/ruby/gems/3.2.0/gems/bundler-2.5.3/lib/bundler/man/bundle-console.1.ronn: conflict markers at lines 2
.venv/lib/python3.12/site-packages/pact/lib/ruby/lib/ruby/gems/3.2.0/gems/bundler-2.5.3/lib/bundler/man/bundle-doctor.1.ronn: conflict markers at lines 2
.venv/lib/python3.12/site-packages/pact/lib/ruby/lib/ruby/gems/3.2.0/gems/bundler-2.5.3/lib/bundler/man/bundle-gem.1.ronn: conflict markers at lines 2
.venv/lib/python3.12/site-packages/pact/lib/ruby/lib/ruby/gems/3.2.0/gems/bundler-2.5.3/lib/bundler/man/bundle-init.1.ronn: conflict markers at lines 2
.venv/lib/python3.12/site-packages/pact/lib/ruby/lib/ruby/gems/3.2.0/gems/bundler-2.5.3/lib/bundler/man/bundle-version.1.ronn: conflict markers at lines 2
.venv/lib/python3.12/site-packages/pact/lib/ruby/lib/ruby/gems/3.2.0/gems/bundler-2.5.3/lib/bundler/man/bundle-plugin.1.ronn: conflict markers at lines 2
.venv/lib/python3.12/site-packages/pact/lib/ruby/lib/ruby/gems/3.2.0/gems/bundler-2.5.3/lib/bundler/man/bundle-info.1.ronn: conflict markers at lines 2
.venv/lib/python3.12/site-packages/pact/lib/ruby/lib/ruby/gems/3.2.0/gems/bundler-2.5.3/lib/bundler/man/bundle-inject.1.ronn: conflict markers at lines 2
.venv/lib/python3.12/site-packages/pact/lib/ruby/lib/ruby/gems/3.2.0/gems/bundler-2.5.3/lib/bundler/man/bundle-exec.1.ronn: conflict markers at lines 2
.venv/lib/python3.12/site-packages/pact/lib/ruby/lib/ruby/gems/3.2.0/gems/bundler-2.5.3/lib/bundler/man/bundle-cache.1.ronn: conflict markers at lines 2
.venv/lib/python3.12/site-packages/pact/lib/ruby/lib/ruby/gems/3.2.0/gems/bundler-2.5.3/lib/bundler/man/bundle-list.1.ronn: conflict markers at lines 2
.venv/lib/python3.12/site-packages/pact/lib/ruby/lib/ruby/gems/3.2.0/gems/bundler-2.5.3/lib/bundler/man/gemfile.5.ronn: conflict markers at lines 2
.venv/lib/python3.12/site-packages/pact/lib/ruby/lib/ruby/gems/3.2.0/gems/bundler-2.5.3/lib/bundler/man/bundle-platform.1.ronn: conflict markers at lines 2
.venv/lib/python3.12/site-packages/pact/lib/ruby/lib/ruby/gems/3.2.0/gems/bundler-2.5.3/lib/bundler/man/bundle-update.1.ronn: conflict markers at lines 2
.venv/lib/python3.12/site-packages/pact/lib/ruby/lib/ruby/gems/3.2.0/gems/bundler-2.5.3/lib/bundler/man/bundle-clean.1.ronn: conflict markers at lines 2
.venv/lib/python3.12/site-packages/pact/lib/ruby/lib/ruby/gems/3.2.0/gems/bundler-2.5.3/lib/bundler/man/bundle-pristine.1.ronn: conflict markers at lines 2
.venv/lib/python3.12/site-packages/pact/lib/ruby/lib/ruby/gems/3.2.0/gems/bundler-2.5.3/lib/bundler/man/bundle-outdated.1.ronn: conflict markers at lines 2
.venv/lib/python3.12/site-packages/pact/lib/ruby/lib/ruby/gems/3.2.0/gems/bundler-2.5.3/lib/bundler/man/bundle-help.1.ronn: conflict markers at lines 2
.venv/lib/python3.12/site-packages/pact/lib/ruby/lib/ruby/gems/3.2.0/gems/bundler-2.5.3/lib/bundler/man/bundle-add.1.ronn: conflict markers at lines 2
.venv/lib/python3.12/site-packages/pact/lib/ruby/lib/ruby/gems/3.2.0/gems/bundler-2.5.3/lib/bundler/man/bundle-binstubs.1.ronn: conflict markers at lines 2
.venv/lib/python3.12/site-packages/pact/lib/ruby/lib/ruby/gems/3.2.0/gems/bundler-2.5.3/lib/bundler/man/bundle.1.ronn: conflict markers at lines 2
.venv/lib/python3.12/site-packages/pact/lib/ruby/lib/ruby/gems/3.2.0/gems/bundler-2.5.3/lib/bundler/man/bundle-install.1.ronn: conflict markers at lines 2
.venv/lib/python3.12/site-packages/pact/lib/ruby/lib/ruby/gems/3.2.0/gems/bundler-2.5.3/lib/bundler/man/bundle-check.1.ronn: conflict markers at lines 2
.venv/lib/python3.12/site-packages/pact/lib/ruby/lib/ruby/3.2.0/rubygems/commands/help_command.rb: conflict markers at lines 85, 149, 163, 178, 197
.venv/lib/python3.12/site-packages/pact/lib/ruby/lib/ruby/3.2.0/rubygems/commands/install_command.rb: conflict markers at lines 68, 84, 126
.venv/lib/python3.12/site-packages/pact/lib/ruby/lib/ruby/3.2.0/bundler/man/bundle-show.1.ronn: conflict markers at lines 2
.venv/lib/python3.12/site-packages/pact/lib/ruby/lib/ruby/3.2.0/bundler/man/bundle-lock.1.ronn: conflict markers at lines 2
.venv/lib/python3.12/site-packages/pact/lib/ruby/lib/ruby/3.2.0/bundler/man/bundle-remove.1.ronn: conflict markers at lines 2
.venv/lib/python3.12/site-packages/pact/lib/ruby/lib/ruby/3.2.0/bundler/man/bundle-viz.1.ronn: conflict markers at lines 2
.venv/lib/python3.12/site-packages/pact/lib/ruby/lib/ruby/3.2.0/bundler/man/bundle-config.1.ronn: conflict markers at lines 2
.venv/lib/python3.12/site-packages/pact/lib/ruby/lib/ruby/3.2.0/bundler/man/bundle-open.1.ronn: conflict markers at lines 2
.venv/lib/python3.12/site-packages/pact/lib/ruby/lib/ruby/3.2.0/bundler/man/bundle-console.1.ronn: conflict markers at lines 2
.venv/lib/python3.12/site-packages/pact/lib/ruby/lib/ruby/3.2.0/bundler/man/bundle-doctor.1.ronn: conflict markers at lines 2
.venv/lib/python3.12/site-packages/pact/lib/ruby/lib/ruby/3.2.0/bundler/man/bundle-gem.1.ronn: conflict markers at lines 2
.venv/lib/python3.12/site-packages/pact/lib/ruby/lib/ruby/3.2.0/bundler/man/bundle-init.1.ronn: conflict markers at lines 2
.venv/lib/python3.12/site-packages/pact/lib/ruby/lib/ruby/3.2.0/bundler/man/bundle-version.1.ronn: conflict markers at lines 2
.venv/lib/python3.12/site-packages/pact/lib/ruby/lib/ruby/3.2.0/bundler/man/bundle-plugin.1.ronn: conflict markers at lines 2
.venv/lib/python3.12/site-packages/pact/lib/ruby/lib/ruby/3.2.0/bundler/man/bundle-info.1.ronn: conflict markers at lines 2
.venv/lib/python3.12/site-packages/pact/lib/ruby/lib/ruby/3.2.0/bundler/man/bundle-inject.1.ronn: conflict markers at lines 2
.venv/lib/python3.12/site-packages/pact/lib/ruby/lib/ruby/3.2.0/bundler/man/bundle-exec.1.ronn: conflict markers at lines 2
.venv/lib/python3.12/site-packages/pact/lib/ruby/lib/ruby/3.2.0/bundler/man/bundle-cache.1.ronn: conflict markers at lines 2
.venv/lib/python3.12/site-packages/pact/lib/ruby/lib/ruby/3.2.0/bundler/man/bundle-list.1.ronn: conflict markers at lines 2
.venv/lib/python3.12/site-packages/pact/lib/ruby/lib/ruby/3.2.0/bundler/man/gemfile.5.ronn: conflict markers at lines 2
.venv/lib/python3.12/site-packages/pact/lib/ruby/lib/ruby/3.2.0/bundler/man/bundle-platform.1.ronn: conflict markers at lines 2
.venv/lib/python3.12/site-packages/pact/lib/ruby/lib/ruby/3.2.0/bundler/man/bundle-update.1.ronn: conflict markers at lines 2
.venv/lib/python3.12/site-packages/pact/lib/ruby/lib/ruby/3.2.0/bundler/man/bundle-clean.1.ronn: conflict markers at lines 2
.venv/lib/python3.12/site-packages/pact/lib/ruby/lib/ruby/3.2.0/bundler/man/bundle-pristine.1.ronn: conflict markers at lines 2
.venv/lib/python3.12/site-packages/pact/lib/ruby/lib/ruby/3.2.0/bundler/man/bundle-outdated.1.ronn: conflict markers at lines 2
.venv/lib/python3.12/site-packages/pact/lib/ruby/lib/ruby/3.2.0/bundler/man/bundle-help.1.ronn: conflict markers at lines 2
.venv/lib/python3.12/site-packages/pact/lib/ruby/lib/ruby/3.2.0/bundler/man/bundle-add.1.ronn: conflict markers at lines 2
.venv/lib/python3.12/site-packages/pact/lib/ruby/lib/ruby/3.2.0/bundler/man/bundle-binstubs.1.ronn: conflict markers at lines 2
.venv/lib/python3.12/site-packages/pact/lib/ruby/lib/ruby/3.2.0/bundler/man/bundle.1.ronn: conflict markers at lines 2
.venv/lib/python3.12/site-packages/pact/lib/ruby/lib/ruby/3.2.0/bundler/man/bundle-install.1.ronn: conflict markers at lines 2
.venv/lib/python3.12/site-packages/pact/lib/ruby/lib/ruby/3.2.0/bundler/man/bundle-check.1.ronn: conflict markers at lines 2
.venv/lib/python3.12/site-packages/pandas/core/base.py: conflict markers at lines 505, 507, 515, 604, 606, 613
.venv/lib/python3.12/site-packages/pandas/core/construction.py: conflict markers at lines 112, 114, 124
.venv/lib/python3.12/site-packages/pandas/__pycache__/__init__.cpython-312.pyc: conflict markers at lines 42
.venv/lib/python3.12/site-packages/pandas/_config/config.py: conflict markers at lines 6, 31
.venv/lib/python3.12/site-packages/pandas/core/__pycache__/construction.cpython-312.pyc: conflict markers at lines 69, 71, 81
.venv/lib/python3.12/site-packages/pandas/core/__pycache__/base.cpython-312.pyc: conflict markers at lines 262, 264, 272, 351, 353, 360
.venv/lib/python3.12/site-packages/pandas/core/dtypes/dtypes.py: conflict markers at lines 1625, 1627, 1633, 1846, 1851
.venv/lib/python3.12/site-packages/pandas/core/arrays/string_.py: conflict markers at lines 238, 240, 244
.venv/lib/python3.12/site-packages/pandas/core/dtypes/__pycache__/dtypes.cpython-312.pyc: conflict markers at lines 733, 735, 741, 805, 810
.venv/lib/python3.12/site-packages/pandas/core/arrays/sparse/array.py: conflict markers at lines 302, 304, 310
.venv/lib/python3.12/site-packages/pandas/core/arrays/__pycache__/string_.cpython-312.pyc: conflict markers at lines 87, 89, 93
.venv/lib/python3.12/site-packages/pandas/core/arrays/sparse/__pycache__/array.cpython-312.pyc: conflict markers at lines 133, 135, 141
.venv/lib/python3.12/site-packages/pandas/io/json/_table_schema.py: conflict markers at lines 71, 73, 81
.venv/lib/python3.12/site-packages/pandas/io/formats/style.py: conflict markers at lines 742, 744, 759, 797, 799, 806, 920, 922, 939
.venv/lib/python3.12/site-packages/pandas/io/json/__pycache__/_table_schema.cpython-312.pyc: conflict markers at lines 33, 35, 43
.venv/lib/python3.12/site-packages/pandas/io/formats/__pycache__/style.cpython-312.pyc: conflict markers at lines 554, 556, 571, 609, 611, 618, 732, 734, 751
.venv/lib/python3.12/site-packages/pandas/_config/__pycache__/config.cpython-312.pyc: conflict markers at lines 14, 39
.venv/lib/python3.12/site-packages/gql/__pycache__/cli.cpython-312.pyc: conflict markers at lines 17
.venv/lib/python3.12/site-packages/sortedcontainers/__pycache__/sorteddict.cpython-312.pyc: conflict markers at lines 11
.venv/lib/python3.12/site-packages/sortedcontainers/__pycache__/sortedset.cpython-312.pyc: conflict markers at lines 9
.venv/lib/python3.12/site-packages/sortedcontainers/__pycache__/sortedlist.cpython-312.pyc: conflict markers at lines 10
.venv/lib/python3.12/site-packages/dill/__pycache__/__info__.cpython-312.pyc: conflict markers at lines 9, 41, 70, 80, 90, 110, 125, 211, 229
.venv/lib/python3.12/site-packages/_pytest/__pycache__/_argcomplete.cpython-312.pyc: conflict markers at lines 27, 39
.venv/lib/python3.12/site-packages/_pytest/__pycache__/pytester.cpython-312.pyc: conflict markers at lines 233, 244
.venv/lib/python3.12/site-packages/_pytest/__pycache__/hookspec.cpython-312.pyc: conflict markers at lines 27, 42, 78, 92, 111, 122, 136, 173, 189, 197, 223, 248, 271, 281, 292, 302, 321, 333, 357, 376, 389, 401, 419, 440, 476, 489, 503, 518, 530, 550, 565, 575, 586, 596, 617, 633, 644, 653, 662, 678, 708, 733, 762, 788, 801, 829, 848, 861, 869, 892, 905, 917
.venv/lib/python3.12/site-packages/psutil/tests/test_unicode.py: conflict markers at lines 9
.venv/lib/python3.12/site-packages/psutil/tests/__pycache__/test_unicode.cpython-312.pyc: conflict markers at lines 11
.venv/lib/python3.12/site-packages/psutil/tests/__pycache__/test_process_all.cpython-312.pyc: conflict markers at lines 60
.venv/lib/python3.12/site-packages/pytest_cov-6.2.1.dist-info/licenses/AUTHORS.rst: conflict markers at lines 3
.venv/lib/python3.12/site-packages/typing_extensions-4.14.1.dist-info/licenses/LICENSE: conflict markers at lines 2, 60
.venv/lib/python3.12/site-packages/beautifulsoup4-4.13.4.dist-info/licenses/AUTHORS: conflict markers at lines 2
.venv/lib/python3.12/site-packages/apscheduler/schedulers/tornado.py: conflict markers at lines 27, 29
.venv/lib/python3.12/site-packages/apscheduler/schedulers/background.py: conflict markers at lines 15, 20
.venv/lib/python3.12/site-packages/apscheduler/schedulers/asyncio.py: conflict markers at lines 25, 27
.venv/lib/python3.12/site-packages/apscheduler/schedulers/twisted.py: conflict markers at lines 26, 28
.venv/lib/python3.12/site-packages/apscheduler/schedulers/__pycache__/twisted.cpython-312.pyc: conflict markers at lines 21, 23
.venv/lib/python3.12/site-packages/apscheduler/schedulers/__pycache__/tornado.cpython-312.pyc: conflict markers at lines 19, 21
.venv/lib/python3.12/site-packages/apscheduler/schedulers/__pycache__/asyncio.cpython-312.pyc: conflict markers at lines 16, 18
.venv/lib/python3.12/site-packages/apscheduler/schedulers/__pycache__/background.cpython-312.pyc: conflict markers at lines 10, 15
.venv/lib/python3.12/site-packages/pip/_vendor/distro/distro.py: conflict markers at lines 214, 216, 250
.venv/lib/python3.12/site-packages/pip/_vendor/distro/__pycache__/distro.cpython-312.pyc: conflict markers at lines 82, 84, 118
.venv/lib/python3.12/site-packages/coverage/__pycache__/plugin.cpython-312.pyc: conflict markers at lines 67, 81, 96
.venv/lib/python3.12/site-packages/google/protobuf/internal/_parameterized.py: conflict markers at lines 81, 97, 111
.venv/lib/python3.12/site-packages/google/protobuf/internal/__pycache__/_parameterized.cpython-312.pyc: conflict markers at lines 78, 94, 108

```
## Ação
Forneça um plano de correção passo a passo.