from core.prompt_builder import iter_generation_prompts
from core.prompt_placeholders import fill_prompt_placeholders
from core.section_parser import parse_requirements_document


def test_marker_is_replaced_with_parsed_requirements():
    filled = fill_prompt_placeholders(
        "Инструкция\n*Тут текст требований*\nКонец",
        requirements_text="3. CRM\nПроверить тариф \\W",
    )
    assert filled == "Инструкция\n3. CRM\nПроверить тариф \\W\nКонец"


def test_prompt_without_marker_stays_the_same():
    original = "Смотри негативные шаги"
    assert (
        fill_prompt_placeholders(original, requirements_text="длинный текст требований")
        == original
    )


def test_blank_requirements_do_not_erase_the_marker():
    original = "До файла *Тут текст требований*"
    assert fill_prompt_placeholders(original, requirements_text="  ") == original


def test_filled_prompt_reaches_generation_without_changing_section_text():
    document = "3. CRM\n1. Проверить тариф\n"
    parsed = parse_requirements_document(document)
    plain = iter_generation_prompts(parsed, extra_prompt="Смотри негативные шаги")
    filled_prompt = fill_prompt_placeholders(
        "Инструкция\n*тут текст требований*",
        requirements_text=document,
    )
    prompts = iter_generation_prompts(parsed, extra_prompt=filled_prompt)
    assert "Проверить тариф" in prompts[0][1]
    assert "*тут текст требований*" not in prompts[0][1].lower()
    assert "3. CRM" in prompts[0][1]
    assert plain[0][1] != prompts[0][1]
