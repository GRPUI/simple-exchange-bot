from typing import List, Dict

from core.db.database_handler import DatabaseHandler
from core.templates.texts import predefined_texts


async def get_texts(
    unique_names: List[str], language_code: str, db: DatabaseHandler
) -> Dict[str, str]:
    """
    Retrieve multiple texts by their unique names.

    :param unique_names: List of texts' unique names to retrieve.
    :param language_code: Language code for the texts.
    :param db: Database handler instance.
    :return: Dictionary mapping unique names to their corresponding text content.
    """
    texts = await db.get_text_items_by_name(unique_names, language_code)

    missing_names = set(unique_names) - set(texts.keys())

    for name in missing_names:
        if name in predefined_texts:
            texts[name] = predefined_texts[name].get(
                language_code, predefined_texts[name]["en"]
            )
        else:
            texts[name] = (
                f"Нужно добавить текст в базу данных для '{name}'."
                if language_code == "ru"
                else f"Text needs to be added to the database for '{name}'."
            )

    return texts
