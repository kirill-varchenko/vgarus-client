import vgarus_client.models


def test_response_without_errors():
    raw = """{"status":200,"message":["infl031098","infl031099","infl031100","infl031101","infl031102","infl031103","infl031104","infl031105","infl031106","infl031107","infl031108","infl031109","infl031110","infl031111","infl031112","infl031113","infl031114","infl031115","infl031116","infl031117"],"errors":"[]"}"""
    resp = vgarus_client.models.VgarusResponse.parse_raw(raw)
    assert resp.status == 200
    assert len(resp.message) == 20
    assert len(resp.errors) == 0


def test_response_with_errors():
    raw = r"""{"status":200,"message":["infl031596","infl031597","infl031598","infl031599","infl031600","infl031601","infl031602","infl031603","infl031604","infl031605","infl031606","infl031607","infl031608","infl031609","infl031610","infl031611","infl031612","infl031613"],"errors":"[\"importJsonNew Error in sample_name: hCoV-19_Russia_OMS-RII-MH130475S_2023: Sample_form. Не верный формат Sample Pick Date, должен быть: ГГГГ-ММ-ДД!\",\"importJsonNew Error in sample_name: hCoV-19_Russia_OMS-RII-MH130474S_2023: Sample_form. Не верный формат Sample Pick Date, должен быть: ГГГГ-ММ-ДД!\"]"}"""
    resp = vgarus_client.models.VgarusResponse.parse_raw(raw)
    assert len(resp.message) == 18
    assert len(resp.errors) == 2
    assert resp.get_errors_virus_names() == [
        "hCoV-19_Russia_OMS-RII-MH130475S_2023",
        "hCoV-19_Russia_OMS-RII-MH130474S_2023",
    ]


def test_response_with_status_not_200():
    raw = r"""{"name":"Bad Request","message":"{\"inputJson\":[\"Элемент sequence в геноме #1 должен быть заполнен строкой\",\"Элемент sequence в геноме #2 должен быть заполнен строкой\",\"Элемент sequence в геноме #3 должен быть заполнен строкой\",\"Элемент sequence в геноме #4 должен быть заполнен строкой\",\"Элемент sequence в геноме #5 должен быть заполнен строкой\",\"Элемент sequence в геноме #6 должен быть заполнен строкой\",\"Элемент sequence в геноме #7 должен быть заполнен строкой\",\"Элемент sequence в геноме #8 должен быть заполнен строкой\",\"Элемент sequence в геноме #9 должен быть заполнен строкой\",\"Элемент sequence в геноме #10 должен быть заполнен строкой\",\"Элемент sequence в геноме #11 должен быть заполнен строкой\",\"Элемент sequence в геноме #12 должен быть заполнен строкой\",\"Элемент sequence в геноме #13 должен быть заполнен строкой\",\"Элемент sequence в геноме #14 должен быть заполнен строкой\",\"Элемент sequence в геноме #15 должен быть заполнен строкой\",\"Элемент sequence в геноме #16 должен быть заполнен строкой\",\"Элемент sequence в геноме #17 должен быть заполнен строкой\",\"Элемент sequence в геноме #18 должен быть заполнен строкой\",\"Элемент sequence в геноме #19 должен быть заполнен строкой\",\"Элемент sequence в геноме #20 должен быть заполнен строкой\"]}","code":0,"status":400}"""
    resp = vgarus_client.models.VgarusResponse.parse_raw(raw)
    assert resp.status == 400
