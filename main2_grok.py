# Walking Simulator: Тени Старого Дома
# Копия логики main.py с переписанной сценой у дома и двумя сценами после.
# Взаимодействие: нумерованные выборы + свободный ввод ключевых слов из описаний.
# Без характеристик: только инвентарь и открытые флаги.

def normalize(text):
    return text.strip().lower()


def has_any(text, *words):
    t = normalize(text)
    return any(w in t for w in words)


def show_inventory(inventory):
    if not inventory:
        print("  (пусто)")
    else:
        for item in sorted(inventory):
            print(f"  - {item}")


def parse_intent(raw):
    """Грубо определяет намерение: осмотреть / взять / использовать / уйти / меню."""
    t = normalize(raw)
    if not t:
        return "empty", t
    if t in ("инвентарь", "вещи", "сумка", "i"):
        return "inventory", t
    if t in ("осмотреться", "осмотр", "look", "о"):
        return "look_around", t
    if t in ("помощь", "help", "?", "х"):
        return "help", t
    if has_any(t, "использовать", "применить", "открыть", "ударить", "вставить", "сломать"):
        return "use", t
    if has_any(t, "взять", "поднять", "подобрать", "забрать"):
        return "take", t
    if has_any(t, "осмотреть", "посмотреть", "глянуть", "заглянуть", "проверить", "трогать", "тронуть"):
        return "examine", t
    if has_any(t, "стучать", "постучать", "стук"):
        return "knock", t
    if has_any(t, "обойти", "двор", "назад", "кругом"):
        return "go_around", t
    if has_any(t, "войти", "войти в", "пройти", "дверь внутрь"):
        return "enter", t
    if has_any(t, "уйти", "уходить", "сбежать", "бежать"):
        return "leave", t
    # Свободный ввод: одно ключевое слово предмета/места — считаем осмотром
    return "keyword", t


def print_help():
    print(
        "\nПодсказка:\n"
        "  • Можно выбрать номер действия (1, 2, 3…)\n"
        "  • Или написать словами, что видишь в описании:\n"
        "      осмотреть дверь / взять камень / использовать ключ\n"
        "  • «осмотреться» — снова показать сцену\n"
        "  • «инвентарь» — что у тебя с собой\n"
        "  • «помощь» — этот текст\n"
        "Предметы и детали нужно заметить в тексте — иначе с ними не поговорить."
    )


# ─────────────────────────────────────────────────────────────
# СЦЕНА 1. Перед домом
# ─────────────────────────────────────────────────────────────

def scene_front(state):
    """Сцена у фасада. Переход: обойти дом → scene_backyard."""
    inventory = state["inventory"]
    flags = state["flags"]

    def describe():
        print("\n" + "─" * 50)
        print("ПЕРЕД ДОМОМ")
        print("─" * 50)
        print(
            "Старый дом стоит на краю пустыря. Крыльцо покосилось, "
            "дверь в тёмной раме закрыта. Рядом — мутное окно; "
            "сквозь грязное стекло едва угадывается комната.\n"
            "У перил валяется ржавый гвоздь. Под ступенями — щель, "
            "куда едва проходит рука. Тропинка уходит вбок, "
            "чтобы обойти дом вокруг."
        )
        if flags.get("note_seen") and not flags.get("note_taken"):
            print("На подоконнике снаружи лежит сложенная записка.")
        if flags.get("knocked"):
            print("После стука изнутри ещё тихо отвечает шорох.")
        print(
            "\nМожно выбрать номер или написать действие "
            "(например: «осмотреть дверь», «взять гвоздь»)."
        )
        print("1. Постучать в дверь")
        print("2. Заглянуть в окно")
        print("3. Обойти дом вокруг")
        print("4. Осмотреться ещё раз")

    describe()

    while True:
        raw = input("\n> ")
        t = normalize(raw)
        intent, _ = parse_intent(raw)

        # Нумерованные выборы
        if t == "1":
            intent = "knock"
            t = "постучать дверь"
        elif t == "2":
            intent = "examine"
            t = "заглянуть окно"
        elif t == "3":
            intent = "go_around"
            t = "обойти дом"
        elif t == "4":
            intent = "look_around"

        if intent == "help":
            print_help()
            continue
        if intent == "inventory":
            print("С собой:")
            show_inventory(inventory)
            continue
        if intent == "look_around" or intent == "empty":
            describe()
            continue
        if intent == "leave":
            print("Уходить сейчас — значит остаться на холоде без ответов. Ты остаёшься.")
            continue

        # ── стук ──
        if intent == "knock" or (intent == "keyword" and has_any(t, "дверь") and has_any(t, "стук", "стучать")):
            print(
                "\nТы стучишь. Звук глухо уходит внутрь. Дверь не открывается — "
                "замок старый, но крепкий. Внутри — тихий шорох, будто кто-то "
                "отошёл от порога."
            )
            flags["knocked"] = True
            if flags.get("note_read"):
                print("Вспоминаешь записку: «Не стучи трижды.» Ты стучал один раз. Пока.")
            continue

        # ── обойти ──
        if intent == "go_around" or has_any(t, "тропинка", "обойти", "кругом"):
            if has_any(t, "тропинка") and intent == "examine":
                print(
                    "\nУзкая тропинка огибает угол дома. Трава примята — "
                    "кто-то ходил здесь недавно. Можно пойти по ней и обойти дом."
                )
                continue
            print(
                "\nТы идёшь по тропинке вдоль стены. Ветер усиливается; "
                "изнутри доносятся неровные звуки. Ты выходишь на задний двор..."
            )
            return "backyard"

        # ── осмотр / ключевые слова ──
        if intent in ("examine", "keyword", "take", "use", "enter"):
            # дверь
            if has_any(t, "дверь", "замок", "крыльцо"):
                if intent == "enter" or has_any(t, "открыть", "войти"):
                    if "ключ" in inventory:
                        print(
                            "\nКлюч входит с трудом и проворачивается. "
                            "Парадная дверь поддаётся..."
                        )
                        flags["entered_front"] = True
                        return "inside"
                    print(
                        "\nДверь заперта. Замок не поддаётся без ключа. "
                        "Можно постучать — или искать другой путь."
                    )
                    continue
                if intent == "use":
                    if "ключ" in inventory and has_any(t, "ключ"):
                        print(
                            "\nТы вставляешь ключ в замок парадной двери. "
                            "Щелчок. Дверь открывается почти беззвучно."
                        )
                        flags["entered_front"] = True
                        flags["used_key_front"] = True
                        return "inside"
                    if "гвоздь" in inventory and has_any(t, "гвоздь"):
                        print(
                            "\nТы ковыряешь замок гвоздём. Металл скрежещет, "
                            "но замок не сдаётся. Нужен настоящий ключ — "
                            "или другой вход."
                        )
                        flags["tried_nail_on_door"] = True
                        continue
                    if "камень" in inventory and has_any(t, "камень"):
                        print(
                            "\nБить камнем по парадной двери слишком шумно и глупо. "
                            "Стекло в окне тоньше — но это уже другой выбор."
                        )
                        continue
                    print("\nЧем именно? Напиши: использовать <предмет> (на дверь).")
                    continue
                print(
                    "\nОбветренная дверь, тёмная рама, тяжёлый замок. "
                    "Петли ржавые. Без ключа внутрь с фасада не попасть. "
                    "Стучать можно — но дом отвечает неохотно."
                )
                continue

            # окно
            if has_any(t, "окно", "стекло", "подоконник"):
                if intent == "use" and "камень" in inventory and has_any(t, "камень"):
                    print(
                        "\nТы размахиваешься камнем… и останавливаешься. "
                        "Бить окно сейчас — привлечь всё, что внутри. "
                        "Камень пока остаётся у тебя."
                    )
                    flags["almost_broke_window"] = True
                    continue
                if intent == "take" and has_any(t, "записк"):
                    pass  # обработаем ниже вместе с запиской
                else:
                    print(
                        "\nТы заглядываешь в мутное окно. Внутри темно, но "
                        "угадывается силуэт человека. Он медленно поворачивается "
                        "к стеклу. Глаза пустые, не враждебные. Силуэт поднимает "
                        "руку и указывает в сторону тропинки — туда, где дом "
                        "можно обойти — затем тает в темноте комнаты."
                    )
                    flags["window_seen"] = True
                    flags["silhouette_seen"] = True
                    if not flags.get("note_taken"):
                        print("На подоконнике снаружи лежит сложенная записка.")
                        flags["note_seen"] = True
                    continue

            # записка
            if has_any(t, "записк"):
                if not flags.get("note_seen") and not flags.get("note_taken"):
                    print("\nКакая записка? Ты пока не замечал ничего такого.")
                    continue
                if flags.get("note_taken") or "записка" in inventory:
                    print(
                        "\nЗаписка у тебя. Выцветшие слова:\n"
                        f"  «{state['name']}… ключ под камнем у яблони. Не стучи трижды.»"
                    )
                    flags["note_read"] = True
                    continue
                if intent == "take" or has_any(t, "взять", "подобрать"):
                    inventory.add("записка")
                    flags["note_taken"] = True
                    flags["note_seen"] = True
                    print(
                        "\nТы берёшь записку. Почерк дрожащий:\n"
                        f"  «{state['name']}… ключ под камнем у яблони. Не стучи трижды.»"
                    )
                    flags["note_read"] = True
                    continue
                print(
                    "\nСложенный клочок бумаги на подоконнике. Можно взять "
                    "или просто прочитать, развернув."
                )
                if intent == "examine":
                    inventory.add("записка")
                    flags["note_taken"] = True
                    flags["note_read"] = True
                    print(
                        f"  «{state['name']}… ключ под камнем у яблони. Не стучи трижды.»\n"
                        "Ты машинально прячешь записку."
                    )
                continue

            # гвоздь
            if has_any(t, "гвоздь"):
                if "гвоздь" in inventory:
                    if intent == "use":
                        print(
                            "\nГвоздь сам по себе никуда не ведёт. "
                            "Можно попробовать использовать гвоздь на дверь или замок."
                        )
                    else:
                        print("\nРжавый гвоздь уже у тебя. Тонкий, острый на конце.")
                    continue
                if intent == "take" or has_any(t, "взять", "подобрать", "поднять"):
                    inventory.add("гвоздь")
                    flags["nail_taken"] = True
                    print("\nТы поднимаешь ржавый гвоздь. Лёгкий, но острый. В карман.")
                    continue
                print(
                    "\nДлинный ржавый гвоздь у перил. Выпал когда-то из доски. "
                    "Можно взять — вдруг пригодится как отмычка или шило."
                )
                continue

            # щель / ступени
            if has_any(t, "щель", "ступен", "подступен", "перил"):
                if has_any(t, "перил") and not has_any(t, "щель", "ступен"):
                    print(
                        "\nПерила шатаются. У основания — тот самый ржавый гвоздь."
                        if "гвоздь" not in inventory
                        else "\nПерила шатаются. Гвоздь ты уже забрал."
                    )
                    continue
                print(
                    "\nПод ступенями темно и сыро. Паутина, земля… "
                    "Рука нащупывает только холод и мелкие камни — ничего полезного."
                )
                flags["checked_under_steps"] = True
                continue

            # дом / фасад
            if has_any(t, "дом", "фасад", "пустыр"):
                print(
                    "\nДом смотрит на тебя тёмными окнами. Кажется, он старше "
                    "любой памяти, что у тебя осталась."
                )
                continue

            if intent == "use":
                print("\nНепонятно, на что применить. Уточни: использовать <что> на <что>.")
                continue
            if intent == "take":
                print("\nЭтого здесь не взять — или ты не назвал предмет из описания.")
                continue

            print(
                "\nТы не находишь такого в поле зрения. Осмотрись внимательнее "
                "или выбери номер действия. («помощь» — подсказка)"
            )
            continue

        print("\nНе понял. Номер действия, ключевое слово из текста или «помощь».")


# ─────────────────────────────────────────────────────────────
# СЦЕНА 2. Задний двор
# ─────────────────────────────────────────────────────────────

def scene_backyard(state):
    """Двор: яблоня, камень, ключ, сарай, задняя дверь → inside."""
    inventory = state["inventory"]
    flags = state["flags"]

    def describe():
        print("\n" + "─" * 50)
        print("ЗАДНИЙ ДВОР")
        print("─" * 50)
        print(
            "Двор зарос. Под старой яблоней лежит тяжёлый камень. "
            "У покосившейся задней двери — ржавый засов. "
            "Чуть в стороне — сарай с мутным зеркалом на стене снаружи, "
            "рядом с косяком. В траве блестит осколок стекла."
        )
        if flags.get("rock_moved") and not flags.get("key_taken"):
            print("Там, где был камень, в ямке что-то тускло блестит.")
        if flags.get("key_taken"):
            print("Ямка под яблоней пуста — ключ ты уже забрал.")
        print(
            "\n1. Вернуться к парадному входу\n"
            "2. Осмотреться\n"
            "3. Подойти к задней двери"
        )

    describe()

    while True:
        raw = input("\n> ")
        t = normalize(raw)
        intent, _ = parse_intent(raw)

        if t == "1":
            print(
                "\nТы возвращаешься по тропинке… но холод и любопытство "
                "гонят обратно во двор. Пока ответы — здесь."
            )
            # Можно было бы вернуть front; по ТЗ — три сцены цепочкой, остаёмся / мягкий отказ
            if "ключ" in inventory:
                go = input("У тебя есть ключ. Открыть парадную дверь с улицы? (да/нет): ")
                if normalize(go) in ("да", "д", "yes", "y"):
                    print("\nТы обходишь дом, вставляешь ключ в парадный замок. Дверь поддаётся.")
                    flags["entered_front"] = True
                    flags["used_key_front"] = True
                    return "inside"
            continue
        if t == "2":
            intent = "look_around"
        if t == "3":
            intent = "examine"
            t = "осмотреть заднюю дверь засов"

        if intent == "help":
            print_help()
            continue
        if intent == "inventory":
            print("С собой:")
            show_inventory(inventory)
            continue
        if intent == "look_around" or intent == "empty":
            describe()
            continue
        if intent == "leave":
            print("Пустырь за двором пуст. Возвращаться некуда — только в дом или к яблоне.")
            continue

        if intent == "knock":
            print("\nТы стучишь в заднюю дверь. Засов дребезжит. Изнутри — тишина тяжелее прежней.")
            flags["knocked_back"] = True
            continue

        if intent in ("examine", "keyword", "take", "use", "enter"):
            # яблоня
            if has_any(t, "яблон", "дерев"):
                print(
                    "\nСтвол в лишайнике, ветки без листьев. Под деревом — "
                    "тяжёлый камень, будто нарочно положенный на что-то."
                )
                continue

            # камень
            if has_any(t, "камень"):
                if "камень" in inventory:
                    if intent == "use":
                        print(
                            "\nКамень у тебя. Можно: использовать камень на засов "
                            "(или на дверь / зеркало)."
                        )
                    else:
                        print("\nТяжёлый булыжник уже в руках / за пазухой — как получилось.")
                    continue
                if intent == "take" or has_any(t, "поднять", "взять", "сдвинуть"):
                    inventory.add("камень")
                    flags["rock_moved"] = True
                    flags["rock_taken"] = True
                    print(
                        "\nТы поднимаешь камень. Под ним — маленькая ямка, "
                        "и в ней тусклый блеск металла."
                    )
                    continue
                if flags.get("rock_moved"):
                    print("\nКамень сдвинут. Ямка открыта.")
                else:
                    print(
                        "\nТяжёлый серый камень. Края вросшие в землю. "
                        "Можно поднять — вдруг что-то спрятано."
                    )
                continue

            # ключ / ямка / блеск
            if has_any(t, "ключ", "ямк", "блеск", "металл"):
                if "ключ" in inventory:
                    print("\nЛатунный ключ уже у тебя. Холодный, тяжёлый для размера.")
                    continue
                if not flags.get("rock_moved"):
                    print(
                        "\nТы не видишь ключа на виду. Может, он спрятан — "
                        "под чем-то тяжёлым у яблони?"
                    )
                    continue
                if intent == "take" or has_any(t, "взять", "подобрать", "достать") or has_any(t, "ключ"):
                    if intent == "examine" and has_any(t, "ямк", "блеск") and not has_any(t, "взять", "ключ"):
                        print(
                            "\nВ ямке — старый латунный ключ. Можно взять."
                        )
                        continue
                    inventory.add("ключ")
                    flags["key_taken"] = True
                    print("\nТы достаёшь латунный ключ. Зубцы стёрты, но форма цела.")
                    continue
                print("\nВ ямке блестит ключ. Стоит взять.")
                continue

            # засов / задняя дверь
            if has_any(t, "засов", "задн", "дверь"):
                if intent == "use" or intent == "enter" or has_any(t, "открыть", "ударить", "сбить"):
                    # ключ на дверь/засов
                    if "ключ" in inventory and (has_any(t, "ключ") or intent == "enter" or has_any(t, "открыть")):
                        if has_any(t, "камень") and "камень" in inventory:
                            pass  # ниже камень
                        else:
                            print(
                                "\nКлюч подходит к секретному отверстию у засова — "
                                "старый хитрый замок. Скрежет. Дверь внутрь поддаётся."
                            )
                            flags["entered_back"] = True
                            flags["used_key_back"] = True
                            return "inside"
                    # камень на засов
                    if "камень" in inventory and has_any(t, "камень", "ударить", "сбить", "сломать"):
                        print(
                            "\nТы бьёшь камнем по засову. Металл звенит и лопается. "
                            "Дверь со скрипом открывается. Где-то в глубине дома "
                            "что-то тяжёлое падает — шум не остался незамеченным."
                        )
                        flags["entered_back"] = True
                        flags["forced_back"] = True
                        return "inside"
                    # гвоздь на засов
                    if "гвоздь" in inventory and has_any(t, "гвоздь"):
                        print(
                            "\nГвоздем засов не сдвинуть — слишком грубый металл. "
                            "Нужен ключ или грубая сила (камень)."
                        )
                        flags["tried_nail_on_bolt"] = True
                        continue
                    if intent == "enter" or has_any(t, "открыть"):
                        if "ключ" in inventory:
                            print(
                                "\nТы открываешь заднюю дверь ключом. Скрип. Темнота коридора."
                            )
                            flags["entered_back"] = True
                            flags["used_key_back"] = True
                            return "inside"
                        print("\nЗасов держится. Нужен ключ — или чем ударить по металлу.")
                        continue
                    print(
                        "\nУкажи предмет: например «использовать ключ на дверь» "
                        "или «использовать камень на засов»."
                    )
                    continue
                print(
                    "\nЗадняя дверь на ржавом засове. Замок хитрый — к нему "
                    "может подойти найденный ключ. Засов можно и сбить, если есть тяжесть."
                )
                continue

            # сарай
            if has_any(t, "сарай"):
                print(
                    "\nСарай пуст: пыль, паутина, запах прели. На внешней стене "
                    "у косяка висит мутное зеркало. Внутри больше нечего брать."
                )
                flags["shed_seen"] = True
                continue

            # зеркало
            if has_any(t, "зеркал"):
                if intent == "use" and "камень" in inventory and has_any(t, "камень"):
                    print(
                        "\nТы бьёшь камень о зеркало. Звон. Отражение на миг "
                        "множится — и гаснет. Осколки сыплются в траву. "
                        "Тишина после этого звонче ветра."
                    )
                    flags["mirror_broken"] = True
                    continue
                if flags.get("mirror_broken"):
                    print("\nРама пуста. Зеркала больше нет.")
                    continue
                print(
                    "\nВ мутном отражении — ты. Губы в стекле шевелятся сами:\n"
                    f"  «{state['name']}… зайди. Пожалуйста.»\n"
                    "Холод пробегает по шее."
                )
                flags["mirror_seen"] = True
                continue

            # осколок
            if has_any(t, "осколок", "стекл"):
                if "осколок" in inventory:
                    print("\nОстрый осколок уже у тебя. Режет палец, если неаккуратно.")
                    continue
                if intent == "take" or has_any(t, "взять", "подобрать"):
                    inventory.add("осколок")
                    flags["shard_taken"] = True
                    print("\nТы осторожно берёшь осколок. Прозрачный, острый. Как маленький нож.")
                    continue
                print("\nОсколок стекла в траве — не от окна дома, скорее от банки. Можно взять.")
                continue

            if intent == "use":
                # общее использование предмета без цели
                if "ключ" in inventory and has_any(t, "ключ"):
                    print("\nКлюч — на дверь или засов. Уточни: использовать ключ на дверь.")
                    continue
                if "камень" in inventory and has_any(t, "камень"):
                    print("\nКамень можно пустить на засов. Например: использовать камень на засов.")
                    continue
                print("\nНеясно, куда применить. Назови предмет и цель из сцены.")
                continue

            if intent == "take":
                print("\nНечего брать с таким именем — или предмет уже у тебя / скрыт.")
                continue

            print("\nЭтого во дворе не видно. «осмотреться» или «помощь».")
            continue

        print("\nНе понял команду. Попробуй иначе или открой «помощь».")


# ─────────────────────────────────────────────────────────────
# СЦЕНА 3. Внутри дома
# ─────────────────────────────────────────────────────────────

def scene_inside(state):
    """Коридор и комната наверху. Столкновения — только по флагам и предметам."""
    inventory = state["inventory"]
    flags = state["flags"]

    def describe():
        print("\n" + "─" * 50)
        print("ВНУТРИ ДОМА")
        print("─" * 50)
        print(
            "Воздух сырой, пахнет старым деревом. Коридор ведёт вглубь. "
            "Слева — проём в гостиную, справа — лестница наверх. "
            "На стене висит выцветший портрет в раме. Под лестницей — "
            "тёмный шкаф. На полу у порога — сухая грязь следов."
        )
        if flags.get("forced_back"):
            print("Где-то в глубине дома ещё звенит эхо падения — тебя услышали.")
        if flags.get("silhouette_seen") and flags.get("knocked"):
            print("Кажется, шорох наверху совпадает с тем силуэтом из окна.")
        print(
            "\n1. Войти в гостиную\n"
            "2. Подняться по лестнице\n"
            "3. Осмотреться\n"
            "4. Уйти из дома"
        )

    describe()

    while True:
        raw = input("\n> ")
        t = normalize(raw)
        intent, _ = parse_intent(raw)

        if t == "1":
            intent = "examine"
            t = "осмотреть гостиную"
        elif t == "2":
            intent = "keyword"
            t = "лестница наверх"
        elif t == "3":
            intent = "look_around"
        elif t == "4":
            intent = "leave"

        if intent == "help":
            print_help()
            continue
        if intent == "inventory":
            print("С собой:")
            show_inventory(inventory)
            continue
        if intent == "look_around" or intent == "empty":
            describe()
            continue

        if intent == "leave" or has_any(t, "уйти", "выйти", "наружу"):
            print(
                "\nТы разворачиваешься и выходишь в холод. Дом остаётся за спиной — "
                "вместе с ответами, до которых ты не дошёл."
            )
            print(f"\nИмя «{state['name']}» ещё звучит в голове.")
            print("\n=== Концовка: Уход ===")
            return "end"

        if intent == "knock":
            print("\nСтучать изнутри некому — разве что самому себе по стене. Глухой стук.")
            continue

        if intent in ("examine", "keyword", "take", "use", "enter", "go_around"):
            # гостиная
            if has_any(t, "гостиная", "гостиную", "камин", "комната"):
                print(
                    "\nМебель под чехлами, камин холодный. На столе — семейная "
                    "фотография: лица размыты, кроме одного. На обороте чернилами:"
                    f" «{state['name']}»."
                )
                flags["living_seen"] = True
                if "записка" in inventory and flags.get("note_read"):
                    print("Почерк на фото — тот же, что на записке с подоконника.")
                    flags["handwriting_match"] = True
                if flags.get("silhouette_seen"):
                    print("У окна изнутри — босые следы в пыли. Кто-то стоял здесь недавно.")
                print("На каминной полке тускнеет медная свеча (огарок).")
                flags["candle_seen"] = True
                continue

            # свеча / огарок
            if has_any(t, "свеч", "огарок"):
                if not flags.get("candle_seen") and not flags.get("living_seen"):
                    print("\nТы не видел свечи. Может, в гостиной?")
                    continue
                if "свеча" in inventory:
                    print("\nОгарок уже у тебя. Фитиль ещё можно зажечь — если будет огонь.")
                    continue
                if intent == "take" or has_any(t, "взять", "подобрать"):
                    inventory.add("свеча")
                    flags["candle_taken"] = True
                    print("\nТы берёшь огарок. Воск крошится в пальцах.")
                    continue
                print("\nКороткий огарок на полке. Можно взять.")
                continue

            # портрет
            if has_any(t, "портрет", "рам", "картин"):
                print(
                    "\nПортрет почти стёрт временем. Под слоем пыли — глаза того же "
                    "силуэта, что в окне. Рама шатается."
                )
                flags["portrait_seen"] = True
                if intent == "take":
                    print("Портрет прибит. Снять с собой не выйдет — только смотреть.")
                if "гвоздь" in inventory and (intent == "use" or has_any(t, "гвоздь")):
                    print(
                        "\nТы поддеваешь раму гвоздём. Сзади, в нише стены, "
                        "лежит тонкая металлическая пластинка — как зубчатый "
                        "фрагмент. Похоже на часть механизма."
                    )
                    flags["portrait_opened"] = True
                    if "пластинка" not in inventory:
                        print("Можно взять пластинку.")
                continue

            # пластинка (после портрета)
            if has_any(t, "пластинка", "механизм", "ниш"):
                if not flags.get("portrait_opened"):
                    print("\nТы не видишь никакой пластинки на виду.")
                    continue
                if "пластинка" in inventory:
                    print("\nЗубчатая пластинка у тебя. К чему-то подходит — но к чему?")
                    continue
                if intent == "take" or has_any(t, "взять"):
                    inventory.add("пластинка")
                    flags["plate_taken"] = True
                    print("\nТы прячешь пластинку. Края острые, узор зубцов знакомо холодит ладонь.")
                    continue
                print("\nВ нише за портретом лежит пластинка. Можно взять.")
                continue

            # шкаф
            if has_any(t, "шкаф"):
                if flags.get("closet_open"):
                    print("\nШкаф уже открыт. Внутри — пустые плечики и запах нафталина.")
                    if flags.get("forced_back") and not flags.get("closet_lurker_done"):
                        # столкновение только по флагу шумного входа
                        print(
                            "Что-то шевелится на нижней полке… Тень дёргается к тебе!"
                        )
                        if "осколок" in inventory or "гвоздь" in inventory:
                            weapon = "осколок" if "осколок" in inventory else "гвоздь"
                            print(
                                f"\nТы машинально вскидываешь {weapon}. Короткий скрежет — "
                                "тень осыпается пылью. Ложная тревога… или нет. "
                                "На полке остаётся только клок ткани."
                            )
                            flags["closet_lurker_done"] = True
                            flags["lurker_repelled"] = True
                        else:
                            print(
                                "\nБез острого предмета в руках ты только захлопываешь дверцу. "
                                "Удар изнутри — и тишина. Больше шкаф не открыть."
                            )
                            flags["closet_lurker_done"] = True
                            flags["lurker_scared"] = True
                    continue
                print(
                    "\nТёмный шкаф под лестницей. Дверца приржавела. "
                    "Можно попробовать открыть шкаф — руками или чем-то тонким."
                )
                if intent == "use" or has_any(t, "открыть", "гвоздь", "осколок", "ключ"):
                    if "гвоздь" in inventory and has_any(t, "гвоздь", "открыть"):
                        print("\nГвоздь как лом: ты отжимаешь дверцу. Скрип. Шкаф открыт.")
                        flags["closet_open"] = True
                        continue
                    if "осколок" in inventory and has_any(t, "осколок", "открыть"):
                        print("\nОсколком поддеваешь защёлку — осторожно, но выходит. Шкаф открыт.")
                        flags["closet_open"] = True
                        continue
                    if "ключ" in inventory and has_any(t, "ключ"):
                        print("\nКлюч к шкафу не подходит — другой механизм.")
                        continue
                    if has_any(t, "открыть"):
                        print(
                            "\nРуками не выходит — защёлка держит. Нужно что-то тонкое: "
                            "гвоздь или осколок."
                        )
                        continue
                continue

            # следы / грязь
            if has_any(t, "след", "гряз"):
                print(
                    "\nСледы ведут от порога к лестнице. Кто-то входил и поднимался — "
                    "не раз. Размер почти как у твоей ноги."
                )
                flags["tracks_seen"] = True
                continue

            # лестница / наверх / силуэт-финал
            if has_any(t, "лестниц", "наверх", "вверх", "комнат", "этаж"):
                print(
                    "\nСтупени скрипят. Наверху — одна дверь, чуть приоткрыта. "
                    "Внутри: кровать, стол, кресло у окна."
                )
                if flags.get("silhouette_seen") or flags.get("mirror_seen"):
                    print(
                        "В кресле — человек. Тот самый силуэт. Он не оборачивается сразу.\n"
                        f"— Я ждал, {state['name']}, — голос как эхо твоего."
                    )
                    flags["met_echo"] = True
                    return ending_encounter(state)
                print(
                    "Кресло пусто. Только отпечаток на пыльной подушке. "
                    "Со стола свешивается край бумаги — пустой лист."
                )
                flags["upstairs_empty"] = True
                if intent == "take" and has_any(t, "бумаг", "лист"):
                    print("Лист пуст. Ты оставляешь его.")
                # Можно закончить «пустым» визитом
                print(
                    "\nДом больше ничего не отдаёт. Ты можешь уйти (напиши «уйти») "
                    "или ещё раз осмотреть нижний этаж."
                )
                continue

            # коридор
            if has_any(t, "коридор", "пол", "стен"):
                print(
                    "\nОбои выцвели. На уровне плеча — царапины, будто кто-то "
                    "шёл, держась за стену."
                )
                continue

            # использовать пластинку / свечу без точной цели
            if intent == "use":
                if "пластинка" in inventory and has_any(t, "пластинка"):
                    if flags.get("met_echo"):
                        print("\nСейчас не до пластинки.")
                    else:
                        print(
                            "\nПластинка никуда не вставляется внизу. "
                            "Может, она для того, кто наверху — или для замка, которого ты не видел."
                        )
                    continue
                if "свеча" in inventory and has_any(t, "свеч"):
                    print(
                        "\nОгня нет. Свеча остаётся холодной. В темноте коридора "
                        "она лишь символ, не свет."
                    )
                    continue
                if "ключ" in inventory and has_any(t, "ключ"):
                    print("\nВнутри дома этому ключу больше нечего открывать — только шкаф, и то не подходит.")
                    continue
                print("\nНекуда применить. Осмотри предметы комнаты и уточни цель.")
                continue

            if intent == "take":
                print("\nНе находится такой вещи под рукой.")
                continue

            print("\nНе замечаешь этого здесь. «осмотреться» покажет доступное.")
            continue

        print("\nНе понял. Номер, слово из описания или «помощь».")


def ending_encounter(state):
    """Финал у силуэта: только открытые флаги и предметы, без характеристик."""
    inventory = state["inventory"]
    flags = state["flags"]
    name = state["name"]

    print(
        "\nОн указывает на пустой стул напротив.\n"
        "1. Сесть и слушать\n"
        "2. Спросить, кто он\n"
        "3. Уйти вниз молча"
    )
    if "камень" in inventory:
        print("4. Сжать камень (показать, что готов к удару)")
    if "записка" in inventory and flags.get("note_read"):
        print("5. Протянуть записку")
    if "пластинка" in inventory:
        print("6. Протянуть пластинку")

    while True:
        raw = input("\n> ")
        t = normalize(raw)

        if t == "3" or has_any(t, "уйти", "вниз", "молча"):
            print(
                f"\nТы спускаешься без слов. За спиной шепчут: «{name}…» — "
                "и дом затихает, как будто обижен."
            )
            print("\n=== Концовка: Молчаливый уход ===")
            return "end"

        if t == "1" or has_any(t, "сесть", "слушать"):
            print(
                f"\nТы садишься. — Добро пожаловать домой, {name}. — "
                "Молчание тёплое. За окном ветер стихает."
            )
            if flags.get("knocked") and not flags.get("note_read"):
                print(
                    "Внизу будто снова стучат — эхо твоего стука. Вы оба слушаете и не двигаетесь."
                )
                print("\n=== Концовка: Порог ===")
            elif flags.get("handwriting_match"):
                print("Он знает, что ты сложил записку и фото. Круг на мгновение смыкается.")
                print("\n=== Концовка: Воссоединение ===")
            else:
                print("\n=== Концовка: Тишина ===")
            return "end"

        if t == "2" or has_any(t, "кто", "спросить"):
            print(
                f"\n— Я — то, что осталось от {name}. Ты ушёл. Я ждал. "
                "Дом держит нас, пока память не сойдётся."
            )
            if flags.get("forced_back"):
                print(
                    "Он хмурится: — Ты вошёл силой. Стены запомнили скрежет. "
                    "Тебе здесь будет теснее, чем другим."
                )
                print("\n=== Концовка: Непрошеный гость ===")
            elif flags.get("mirror_broken"):
                print(
                    "— Ты разбил зеркало. Отражений меньше. Может, так и лучше."
                )
                print("\n=== Концовка: Без отражения ===")
            else:
                print("\n=== Концовка: Эхо ===")
            return "end"

        if (t == "4" or has_any(t, "камень", "удар")) and "камень" in inventory:
            print(
                "\nТы сжимаешь камень. Он видит. — Если ударишь — останешься один. "
                "Если отпустишь — останемся вместе."
            )
            hit = input("Ударить? (да/нет): ")
            if normalize(hit) in ("да", "д", "yes", "y"):
                print(
                    "\nКамень стукается о пол. Кресло пусто. В доме только ты."
                )
                print("\n=== Концовка: Один ===")
            else:
                print(
                    f"\nТы разжимаешь пальцы. — Храбрый выбор, {name}. — Свет в окне теплеет."
                )
                print("\n=== Концовка: Доверие ===")
            return "end"

        if (t == "5" or has_any(t, "записк")) and "записка" in inventory:
            print(
                "\nОн разворачивает записку, которую сам когда-то оставил — или ты. "
                "Улыбка усталая. — Значит, ключ ты нашёл. Значит, можно не ждать вечно."
            )
            if flags.get("window_seen"):
                print("Жест у окна и эти строки складываются в одну линию.")
            print("\n=== Концовка: Письмо доставлено ===")
            return "end"

        if (t == "6" or has_any(t, "пластинка")) and "пластинка" in inventory:
            print(
                "\nОн берёт пластинку и вставляет в щель подлокотника кресла. "
                "Щелчок, как у замка. В стене открывается узкая ниша — "
                "пустая, но пахнет дождём и улицей, не сыростью дома."
            )
            print(
                f"— Выход, о котором я забыл, {name}. Можешь идти. "
                "Или остаться. Оба пути честны."
            )
            choice = input("Выйти через нишу? (да/нет): ")
            if normalize(choice) in ("да", "д", "yes", "y"):
                print(
                    "\nТы проходишь в запах дождя. Дом остаётся сном за спиной."
                )
                print("\n=== Концовка: Скрытый выход ===")
            else:
                print(
                    "\nТы остаёшься. Ниша медленно закрывается. Кресло скрипит рядом."
                )
                print("\n=== Концовка: Осознанный круг ===")
            return "end"

        # Свободный ввод без номера
        if has_any(t, "камень") and "камень" not in inventory:
            print("\nКамня у тебя нет.")
            continue
        if has_any(t, "записк") and "записка" not in inventory:
            print("\nЗаписки у тебя нет.")
            continue
        if has_any(t, "осколок") and "осколок" in inventory:
            print(
                "\nТы показываешь осколок. Он качает головой: — Не для меня. "
                "Для шкафа и страхов внизу."
            )
            continue
        if flags.get("lurker_repelled") and has_any(t, "шкаф", "тень", "ткан"):
            print("\n— Ты уже прогнал то, что жило внизу. Спасибо. Редко кто спускается с остротой в руке.")
            continue

        print("\nВыбери номер из списка или назови действие с предметом, который у тебя есть.")


# ─────────────────────────────────────────────────────────────
# Точка входа
# ─────────────────────────────────────────────────────────────

def main():
    print("=== Тени Старого Дома ===")
    print()
    print(
        "Ты не можешь вспомнить последний день. Не можешь вспомнить, как оказался "
        "перед этим старым домом. Ветер свистит сквозь щели, и кажется, что дом "
        "наблюдает за тобой. На улице слишком холодно, чтобы долго здесь оставаться. "
        "Обветренная одежда почти прилипает к исхудалому скелету твоего тела. "
        "Ты чувствуешь, что должен сделать выбор, прежде чем станет слишком поздно "
        "и последний мускул не откажет.\n"
        "Единственная мысль, которая не даёт тебе покоя здесь и сейчас — Имя... "
        "Чьё имя? Может быть, твоё собственное? Того, кто невзначай привёл тебя сюда? "
        "Или того, кто когда-то жил в этом доме?"
    )

    name = input("\nКак меня зовут? ").strip()
    if not name:
        name = "Незнакомец"

    state = {
        "name": name,
        "inventory": set(),
        "flags": {},
    }

    print(f"\nТы шепчешь: «{name}»… Слово звучит чужим, но ты решаешь держаться за него.")
    print("Ты делаешь шаг вперёд — к старому дому.")
    print("(Набери «помощь», если неясно, как действовать.)")

    scene = "front"
    while scene != "end":
        if scene == "front":
            scene = scene_front(state)
        elif scene == "backyard":
            scene = scene_backyard(state)
        elif scene == "inside":
            scene = scene_inside(state)
        else:
            break

    inv = state["inventory"]
    if inv:
        print("\nС собой в конце было: " + ", ".join(sorted(inv)) + ".")
    print("Спасибо за игру.")


if __name__ == "__main__":
    main()
