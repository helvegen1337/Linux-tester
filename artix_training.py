
import smtplib
import os
import random
import datetime
import re
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- ЦВЕТОВЫЕ КОДЫ ДЛЯ КРАСИВОГО ВЫВОДА ---
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    BLUE = '\033[34m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    RED = '\033[31m'
    PURPLE = '\033[35m'
    CYAN = '\033[36m'

# --- СЕКЦИЯ КОНФИГУРАЦИ-И ---

RECIPIENT_EMAIL = "support@linux-training.com"
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = os.getenv("SMTP_PORT", 587)
SMTP_LOGIN = os.getenv("SMTP_LOGIN")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

SESSION_LOG = []
USER_PROGRESS = {}
CURRENT_USER = ""

# --- УПРАВЛЕНИЕ ДАННЫМИ ---

def load_training_data():
    """Загружает учебные данные из JSON-файла."""
    try:
        with open('training_data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"{Colors.FAIL}Ошибка: Файл training_data.json не найден.{Colors.ENDC}")
        return None
    except json.JSONDecodeError:
        print(f"{Colors.FAIL}Ошибка: Неверный формат JSON в файле training_data.json.{Colors.ENDC}")
        return None

def load_user_progress():
    """Загружает прогресс пользователей."""
    global USER_PROGRESS
    try:
        with open('user_progress.json', 'r', encoding='utf-8') as f:
            USER_PROGRESS = json.load(f)
    except FileNotFoundError:
        USER_PROGRESS = {}

def save_user_progress():
    """Сохраняет прогресс пользователей."""
    with open('user_progress.json', 'w', encoding='utf-8') as f:
        json.dump(USER_PROGRESS, f, indent=4, ensure_ascii=False)

TRAINING_DATA = load_training_data()

# --- СИСТЕМА ДОСТИЖЕНИЙ ---

ACHIEVEMENTS = {
    "first_steps": {
        "name": "🎯 Первые шаги",
        "description": "Выполнить первое задание",
        "condition": lambda progress: len(progress.get('completed_tasks', [])) >= 1
    },
    "quick_learner": {
        "name": "🚀 Быстрый ученик",
        "description": "Выполнить 5 заданий за одну сессию",
        "condition": lambda progress: len(progress.get('completed_tasks', [])) >= 5
    },
    "master_of_basics": {
        "name": "📚 Мастер основ",
        "description": "Завершить все задания в модуле 'Основы'",
        "condition": lambda progress: check_module_completion(progress, "1")
    },
    "test_champion": {
        "name": "🏆 Чемпион тестирования",
        "description": "Получить 100% в любом тесте",
        "condition": lambda progress: any(result.get('score', 0) == 100 for result in progress.get('test_results', {}).values())
    },
    "persistent_student": {
        "name": "💪 Настойчивый студент",
        "description": "Заниматься 5 дней подряд",
        "condition": lambda progress: check_consecutive_days(progress)
    }
}

def check_module_completion(progress, module_id):
    """Проверяет завершение всех заданий в модуле."""
    if not TRAINING_DATA or module_id not in TRAINING_DATA:
        return False
    
    module_tasks = set()
    completed_tasks = set(progress.get('completed_tasks', []))
    
    for cmd_data in TRAINING_DATA[module_id].get('commands', {}).values():
        for task in cmd_data.get('practice', []):
            module_tasks.add(task['task'])
    
    return module_tasks.issubset(completed_tasks)

def check_consecutive_days(progress):
    """Проверяет количество последовательных дней занятий."""
    sessions = progress.get('session_stats', {}).get('sessions', [])
    if not sessions:
        return False
    
    # Конвертируем строки дат в объекты datetime
    dates = sorted([datetime.datetime.strptime(s['date'], "%Y-%m-%d") for s in sessions])
    
    # Ищем максимальную последовательность
    max_streak = current_streak = 1
    for i in range(1, len(dates)):
        if (dates[i] - dates[i-1]).days == 1:
            current_streak += 1
            max_streak = max(max_streak, current_streak)
        else:
            current_streak = 1
            
    return max_streak >= 5

def check_achievements(user_progress):
    """Проверяет и обновляет достижения пользователя."""
    if 'achievements' not in user_progress:
        user_progress['achievements'] = []
        
    new_achievements = []
    for achievement_id, achievement in ACHIEVEMENTS.items():
        if (achievement_id not in user_progress['achievements'] and 
            achievement['condition'](user_progress)):
            user_progress['achievements'].append(achievement_id)
            new_achievements.append(achievement)
            
    return new_achievements

# --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ---

def log_action(message, category="INFO"):
    """Логирует действия пользователя с категорией и временной меткой.
    
    Args:
        message (str): Сообщение для логирования
        category (str): Категория сообщения (INFO, SUCCESS, WARNING, ERROR)
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    category_colors = {
        "INFO": Colors.BLUE,
        "SUCCESS": Colors.OKGREEN,
        "WARNING": Colors.YELLOW,
        "ERROR": Colors.PURPLE
    }
    color = category_colors.get(category, Colors.ENDC)
    
    log_entry = {
        "timestamp": timestamp,
        "user": CURRENT_USER,
        "category": category,
        "message": message
    }
    
    formatted_entry = f"[{timestamp}] [{color}{category}{Colors.ENDC}] [{CURRENT_USER}] {message}"
    SESSION_LOG.append(formatted_entry)
    
    # Сохраняем лог в файл
    try:
        with open('training_log.txt', 'a', encoding='utf-8') as f:
            f.write(formatted_entry + '\n')
    except Exception as e:
        print(f"{Colors.PURPLE}Ошибка при сохранении лога: {e}{Colors.ENDC}")

def send_report_email():
    """Отправляет отчет о сессии на почту."""
    pass

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def wait_for_enter():
    input(f"\n{Colors.CYAN}Нажмите Enter, чтобы продолжить...{Colors.ENDC}")

def check_answer(user_answer, task_data):
    """
    Проверяет ответ пользователя, давая контекстные подсказки.
    Возвращает (bool, str): (корректность, сообщение).
    """
    correct_answer = task_data['solution']
    user_clean = ' '.join(user_answer.lower().split())
    correct_clean = ' '.join(correct_answer.lower().split())

    # 1. Прямое совпадение
    if user_clean == correct_clean:
        return True, f"{Colors.OKGREEN}Правильно!{Colors.ENDC}"

    # 2. Симуляция распространенных ошибок из training_data.json
    if 'error_simulation' in task_data:
        for sim in task_data['error_simulation']:
            if user_clean == sim['wrong_input'].lower():
                log_action(f"Пользователь допустил симулированную ошибку: {sim['wrong_input']}")
                return False, f"{Colors.FAIL}Неправильно. {sim['message']}{Colors.ENDC}"

    # 3. Общие контекстные подсказки
    if user_clean.startswith("sudo "):
        return False, f"Неправильно. {Colors.YELLOW}Подсказка: Права суперпользователя (sudo) здесь не требуются.{Colors.ENDC}"
    if '"' in user_answer or "'" in user_answer:
        if '"' not in correct_answer and "'" not in correct_answer:
            return False, f"Неправильно. {Colors.YELLOW}Подсказка: В этой команде кавычки не нужны.{Colors.ENDC}"

    # Подсказка для rm -r
    if correct_clean.startswith("rm -r") and not user_clean.startswith("rm -r") and user_clean.startswith("rm "):
         return False, f"Неправильно. {Colors.YELLOW}Подсказка: Для удаления директорий используется флаг '-r'.{Colors.ENDC}"

    # Общий ответ, если ничего не подошло
    log_action(f"Неправильный ответ. Пользователь: '{user_answer}', Ожидалось: '{correct_answer}'")
    return False, f"Неправильно. Правильный ответ: {Colors.OKBLUE}{correct_answer}{Colors.ENDC}"

# --- ФУНКЦИИ МЕНЮ (ПЕРЕРАБОТАННЫЕ) ---

def run_practice_session(command_data):
    """
    Запускает практическое задание, начиная с самого легкого из нерешенных.
    """
    completed_tasks = USER_PROGRESS[CURRENT_USER].get('completed_tasks', [])
    unsolved_tasks = [
        t for t in command_data.get('practice', [])
        if t['task'] not in completed_tasks
    ]

    if not unsolved_tasks:
        print(f"{Colors.YELLOW}Вы решили все задания для этой команды!{Colors.ENDC}")
        wait_for_enter()
        return

    # Находим минимальный уровень сложности среди нерешенных задач
    min_difficulty = min(t['difficulty'] for t in unsolved_tasks)
    
    # Отбираем только задачи этого уровня
    tasks_to_ask = [t for t in unsolved_tasks if t['difficulty'] == min_difficulty]
    
    task_data = random.choice(tasks_to_ask)

    clear_screen()
    print(f"{Colors.HEADER}--- Практика: {command_data['name']} ---{Colors.ENDC}")
    print(f"{Colors.BOLD}Уровень сложности: {min_difficulty}{Colors.ENDC}\n")
    print(f"{Colors.CYAN}Задание:{Colors.ENDC}\n{task_data['task']}\n")
    
    user_answer = input(f"{Colors.YELLOW}Ваш ответ:{Colors.ENDC} ")
    log_action(f"Пользователь ввел ответ: '{user_answer}' для задания: '{task_data['task']}'")
    
    is_correct, message = check_answer(user_answer, task_data)
    
    print(f"\n{message}\n")
    
    if is_correct:
        # Инициализируем структуру прогресса, если её нет
        if CURRENT_USER not in USER_PROGRESS:
            USER_PROGRESS[CURRENT_USER] = {}
        
        # Инициализируем список выполненных заданий
        if 'completed_tasks' not in USER_PROGRESS[CURRENT_USER]:
            USER_PROGRESS[CURRENT_USER]['completed_tasks'] = []
        
        # Добавляем задание в список выполненных
        if task_data['task'] not in USER_PROGRESS[CURRENT_USER]['completed_tasks']:
            USER_PROGRESS[CURRENT_USER]['completed_tasks'].append(task_data['task'])
        save_user_progress()
        log_action(f"Задание '{task_data['task']}' отмечено как выполненное.")
        
        if 'explanation' in task_data:
            print(f"{Colors.OKGREEN}Пояснение:{Colors.ENDC} {task_data['explanation']}")
    else:
        log_action("Ответ неправильный.")
        wait_for_enter()

def run_test_session():
    """Запускает сессию тестирования."""
    clear_screen()
    print(f"{Colors.HEADER}{Colors.BOLD}--- Тестирование ---{Colors.ENDC}\n")
    print("Выберите тест:\n")
    print(f"{Colors.GREEN}1. Новичок{Colors.ENDC} - базовые команды и простые операции")
    print(f"{Colors.YELLOW}2. Что-то понимаю{Colors.ENDC} - продвинутые команды и сценарии")
    print(f"{Colors.RED}3. Овладел коровьей СуперСилой{Colors.ENDC} - экспертный уровень")
    print(f"{Colors.PURPLE}4. 📁 Знание файловой системы{Colors.ENDC} - структура каталогов и логи")
    print(f"{Colors.BLUE}5. 🏪 Работа с кассовой системой (РМК){Colors.ENDC} - кассовые операции и учет")
    print(f"{Colors.CYAN}6. 🖥️ Control Center{Colors.ENDC} - управление и мониторинг")
    print("------------------------------------------")
    print(" 0. Назад")
    print("------------------------------------------")

    level_choice = input("\nВыберите тест: ")
    if level_choice == '0':
        return
    elif level_choice in ['1', '2', '3', '4', '5', '6']:
        run_level_test(int(level_choice))
    else:
        print(f"\n{Colors.FAIL}Неверный выбор.{Colors.ENDC}")
        wait_for_enter()

def run_level_test(level):
    """Запускает тест определенного уровня."""
    test_level_data = TRAINING_DATA.get('tests', {}).get(str(level), {})
    if not test_level_data or 'questions' not in test_level_data:
        print(f"{Colors.YELLOW}Тесты для этого уровня пока не добавлены.{Colors.ENDC}")
        wait_for_enter()
        return

    questions = test_level_data['questions']
    total_questions = len(questions)
    correct_answers = 0
    
    for i, question in enumerate(questions, 1):
        clear_screen()
        print(f"{Colors.HEADER}Вопрос {i} из {total_questions}{Colors.ENDC}\n")
        print(f"{Colors.CYAN}{question['question']}{Colors.ENDC}\n")
        
        # Показываем варианты ответов
        options = question['options']
        for j, option in enumerate(options):
            print(f"{Colors.YELLOW}{j + 1}. {option}{Colors.ENDC}")
        
        print(f"\n{Colors.BLUE}Введите номер правильного ответа (1-{len(options)}) или 0 для выхода{Colors.ENDC}")
        
        while True:
            user_input = input(f"\n{Colors.YELLOW}Ваш ответ:{Colors.ENDC} ").strip()
            
            # Проверяем на выход
            if user_input == '0' or user_input.lower() in ['exit', 'quit', 'выход']:
                print(f"\n{Colors.WARNING}Тест прерван.{Colors.ENDC}")
                if i > 1:  # Если ответили хотя бы на один вопрос
                    answered_questions = i - 1
                    partial_score = (correct_answers / answered_questions) * 100
                    print(f"\n{Colors.CYAN}Промежуточные результаты:{Colors.ENDC}")
                    print(f"Отвечено на {answered_questions} из {total_questions} вопросов")
                    print(f"Правильных ответов: {correct_answers}")
                    print(f"Процент успеха: {partial_score:.1f}%")
                print(f"\n{Colors.YELLOW}Возвращаемся в главное меню.{Colors.ENDC}")
                wait_for_enter()
                return
            
            try:
                user_answer = int(user_input) - 1  # Преобразуем в индекс (0-based)
                if user_answer < 0 or user_answer >= len(options):
                    print(f"{Colors.FAIL}Введите число от 1 до {len(options)} или 0 для выхода{Colors.ENDC}")
                    continue
                
                correct_index = question['correct']
                if user_answer == correct_index:
                    correct_answers += 1
                    print(f"\n{Colors.OKGREEN}Правильно!{Colors.ENDC}")
                else:
                    print(f"\n{Colors.FAIL}Неправильно.{Colors.ENDC}")
                
                print(f"\n{Colors.BOLD}Правильный ответ:{Colors.ENDC} {options[correct_index]}")
                print(f"\n{Colors.CYAN}Объяснение:{Colors.ENDC} {question['explanation']}")
                wait_for_enter()
                break
                
            except ValueError:
                print(f"{Colors.FAIL}Введите число от 1 до {len(options)} или 0 для выхода{Colors.ENDC}")
                continue
    
    # Показываем результат
    clear_screen()
    score_percentage = (correct_answers / total_questions) * 100
    print(f"{Colors.HEADER}Результаты тестирования:{Colors.ENDC}\n")
    print(f"Правильных ответов: {correct_answers} из {total_questions}")
    print(f"Процент успеха: {score_percentage:.1f}%\n")
    
    if score_percentage >= 90:
        print(f"{Colors.OKGREEN}Отлично! Вы действительно хорошо разбираетесь в этой теме!{Colors.ENDC}")
    elif score_percentage >= 70:
        print(f"{Colors.YELLOW}Хороший результат! Но есть куда расти.{Colors.ENDC}")
    else:
        print(f"{Colors.RED}Стоит еще попрактиковаться. Не сдавайтесь!{Colors.ENDC}")
    
    # Сохраняем результат
    test_results = USER_PROGRESS[CURRENT_USER].setdefault('test_results', {})
    test_results[str(level)] = {
        'score': score_percentage,
        'completed_at': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    save_user_progress()
    wait_for_enter()

def run_scenario_session():
    """Запускает сессию с практическими сценариями."""
    clear_screen()
    print(f"{Colors.HEADER}{Colors.BOLD}--- Практические сценарии ---{Colors.ENDC}\n")
    
    # Загружаем сценарии из конфигурации
    scenarios = TRAINING_DATA.get('scenarios', {})
    if not scenarios:
        print(f"{Colors.YELLOW}Сценарии пока не добавлены в базу данных.{Colors.ENDC}")
        wait_for_enter()
        return
    
    while True:
        clear_screen()
        print(f"{Colors.HEADER}Доступные сценарии:{Colors.ENDC}\n")
        
        # Показываем список доступных сценариев
        for scenario_id, scenario_data in scenarios.items():
            completed = scenario_data['id'] in USER_PROGRESS[CURRENT_USER].get('completed_scenarios', [])
            status = f"{Colors.OKGREEN}[✓]" if completed else f"{Colors.WARNING}[ ]"
            print(f" {scenario_id}. {Colors.CYAN}{scenario_data['name']}{Colors.ENDC} {status}")
            print(f"    Сложность: {Colors.YELLOW}{'★' * scenario_data['difficulty']}{Colors.ENDC}")
            print(f"    {scenario_data['description']}\n")
        
        print("------------------------------------------")
        print(" 0. Назад")
        print("------------------------------------------")
        
        choice = input("\nВыберите сценарий: ")
        if choice == '0':
            break
            
        if choice in scenarios:
            run_single_scenario(scenarios[choice])
        else:
            print(f"\n{Colors.FAIL}Неверный выбор сценария.{Colors.ENDC}")
            wait_for_enter()

def run_single_scenario(scenario_data):
    """Запускает отдельный сценарий."""
    clear_screen()
    print(f"{Colors.HEADER}--- {scenario_data['name']} ---{Colors.ENDC}\n")
    print(f"{Colors.BOLD}Описание:{Colors.ENDC}\n{scenario_data['description']}\n")
    print(f"{Colors.BOLD}Сложность:{Colors.ENDC} {scenario_data['difficulty']}/5\n")
    
    # Показываем задания сценария
    for step_num, step in enumerate(scenario_data['steps'], 1):
        print(f"\n{Colors.CYAN}Шаг {step_num}:{Colors.ENDC}")
        print(step['task'])
        
        while True:
            user_answer = input(f"\n{Colors.YELLOW}Ваше решение [{Colors.BOLD}help{Colors.ENDC}{Colors.YELLOW} для подсказки, {Colors.BOLD}skip{Colors.ENDC}{Colors.YELLOW} для пропуска]:{Colors.ENDC} ")
            
            if user_answer.lower() == 'help':
                print(f"\n{Colors.BLUE}Подсказка:{Colors.ENDC} {step['hint']}")
                continue
                
            if user_answer.lower() == 'skip':
                print(f"\n{Colors.WARNING}Шаг пропущен. Правильное решение: {Colors.BOLD}{step['solution']}{Colors.ENDC}")
                break
                
            is_correct, message = check_answer(user_answer, {'solution': step['solution']})
            print(f"\n{message}")
            
            if is_correct:
                if 'explanation' in step:
                    print(f"\n{Colors.OKGREEN}Объяснение:{Colors.ENDC} {step['explanation']}")
                break
            else:
                print(f"\n{Colors.YELLOW}Введите 'help' для подсказки или попробуйте снова.{Colors.ENDC}")
    
    # Отмечаем сценарий как выполненный
    completed_scenarios = USER_PROGRESS[CURRENT_USER].setdefault('completed_scenarios', [])
    if scenario_data['id'] not in completed_scenarios:
        completed_scenarios.append(scenario_data['id'])
        save_user_progress()
        print(f"\n{Colors.OKGREEN}Поздравляем! Сценарий успешно завершен!{Colors.ENDC}")
    
        wait_for_enter()

def show_guidance():
    """Показывает напутственное сообщение и информацию о командах помощи."""
    clear_screen()
    print(f"{Colors.HEADER}{Colors.BOLD}--- Напутствие и команды помощи ---{Colors.ENDC}\n")
    
    # Напутственное сообщение
    print(f"{Colors.CYAN}---------------------------------------------------------------------------------------------------------------------------------{Colors.ENDC}\n")
    print(f"{Colors.YELLOW}Линукс - это как прыгнуть в прорубь, в основном он приносит боль. Это как сложнfz hardcore RPG и ты попал в  локация высокоуровневых боссов в перемешку с мелкими. Никогда не угадаешь.{Colors.ENDC}\n")
    print(f"{Colors.GREEN}Секрет здесь в том, что каким бы сложным тебе не казалась твоя задача - ты в состоянии ее решить. Только заспанившись ты можешь валить жестких боссов и черпать кучу xp.{Colors.ENDC}\n")
    print(f"{Colors.PURPLE}Только страдания даруют силу и мудрость.{Colors.ENDC}\n")
    print(f"{Colors.BLUE}Не пренебрегай чем-то эффективным в сторону знакомого.{Colors.ENDC}\n")
    print(f"{Colors.CYAN}В начале - ты не почувствуешь разницу, но чем выше будет уровень - тем больше вредных привычек ты заимеешь.{Colors.ENDC}\n")
    
    print(f"{Colors.YELLOW}Что бы выполнять наши задачи внедрения – тебе хватит mc и команд 20 + документация, но ты наверняка хочешь делать свою работу быстро и всегда иметь в запасе выигранное время. Ведь так?{Colors.ENDC}\n")
    print(f"{Colors.RED}Тогда я хочу повести тебя через твой кошмар – ПРИВЫКАЙ РАБОТАТЬ БЕЗ MC. Любая графика отнимает твою скорость, а специфика у нас такая... что порой нужно провести огромное количество действий одновременно и на сервере и на кассе и в БД залезть.{Colors.ENDC}\n")
    print(f"{Colors.GREEN}Чем сильнее ты овладеешь искусством \"бесконтактного боя\" – тем быстрее пойдет твоя работа.{Colors.ENDC}\n")
    
    print(f"{Colors.BOLD}.{Colors.ENDC}\n")
    print(f"{Colors.CYAN}Главное – понять и выбрать решение, а команды можно так компоновать, что по своей сути – ты можешь выполнить все что угодно и без остановки. На первый взгляд простые команды – самые полезные.{Colors.ENDC}\n")
    print(f"{Colors.YELLOW}Потоки STDIN STDERROR STDOUT – то что отличает новичка от продвинутого пользователя. Удели этому больше времени, а я в тесты вмонтирую множество сценариев где это пригодится.{Colors.ENDC}\n")
    
    print(f"{Colors.BLUE}Я делал все не самым равномерным способом, но старался соблюдать тенденцию от малого к большему. Теорию почитаешь вне этой утилиты. В любом случае – проходи ВСЕ, затыки – спрашивай!{Colors.ENDC}\n")
    print(f"{Colors.GREEN}А я буду видоизменять утилитку и добавлять тебе задания на которых были просадки. Консультировать по отдельным вопросам. Все это сработает – если ты горишь желанием.{Colors.ENDC}\n")
    print(f"{Colors.BOLD}Если у тебя получится собрать все баллы здесь, пройти все тесты и весь теор. материал, я тебе обещаю – ты будешь ГОРИЛЛОЙ в этих джунглях. Надеюсь твоя вера в себя, так же крепка – как я верю в тебя.{Colors.ENDC}\n")
    print(f"{Colors.HEADER}--- Важные команды помощи ---{Colors.ENDC}\n")
    print(f"{Colors.BOLD}man <команда>{Colors.ENDC} - показывает полное руководство по команде")
    print("Пример: man ls - покажет все возможные параметры и варианты использования команды ls\n")
    print(f"{Colors.BOLD}<команда> --help{Colors.ENDC} или {Colors.BOLD}<команда> -h{Colors.ENDC} - показывает краткую справку")
    print("Пример: ls --help - покажет основные параметры команды ls\n")
    print(f"{Colors.YELLOW}Совет: Всегда проверяйте параметры команд через man или --help перед использованием!{Colors.ENDC}")
    wait_for_enter()

def show_user_progress():
    """Показывает статистику текущего пользователя."""
    clear_screen()
    
    # Создаем заголовок с именем пользователя
    title = f" Прогресс пользователя: {CURRENT_USER} "
    padding = "═" * ((60 - len(title)) // 2)
    print(f"{Colors.HEADER}╔{padding}{title}{padding}╗{Colors.ENDC}")
    print(f"{Colors.HEADER}║{' ' * (len(padding)*2 + len(title))}║{Colors.ENDC}")

    # Показываем общий прогресс
    completed_tasks = USER_PROGRESS[CURRENT_USER].get('completed_tasks', [])
    total_tasks = sum(
        len(cmd.get('practice', []))
        for mod in TRAINING_DATA.values()
        if isinstance(mod, dict) and 'commands' in mod
        for cmd in mod['commands'].values()
    )
    
    if total_tasks > 0:
        total_percentage = (len(completed_tasks) / total_tasks) * 100
        progress_bar = create_progress_bar(total_percentage)
        print(f"{Colors.HEADER}║{Colors.ENDC} {Colors.BOLD}{Colors.PURPLE}ОБЩИЙ ПРОГРЕСС:{Colors.ENDC}")
        print(f"{Colors.HEADER}║{Colors.ENDC} {progress_bar}")
        print(f"{Colors.HEADER}║{Colors.ENDC} Выполнено задач: {Colors.CYAN}{len(completed_tasks)}/{total_tasks}{Colors.ENDC} ({Colors.YELLOW}{total_percentage:.1f}%{Colors.ENDC})")
        print(f"{Colors.HEADER}║{Colors.ENDC}")

    # Показываем результаты тестов
    test_results = USER_PROGRESS[CURRENT_USER].get('test_results', {})
    if test_results:
        print(f"{Colors.HEADER}║{Colors.ENDC} {Colors.BOLD}{Colors.BLUE}РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:{Colors.ENDC}")
        levels = {
            "1": "🌱 Новичок",
            "2": "🌿 Что-то понимаю", 
            "3": "🌳 ВОЛОСАТАЯ ГОРИЛЛА",
            "4": "📁 Знание файловой системы",
            "5": "🏪 Работа с кассовой системой (РМК)",
            "6": "🖥️ Control Center"
        }
        for level, result in test_results.items():
            if level not in levels:
                continue
            score = result.get('score', 0)
            completed_at = result.get('completed_at', 'Неизвестно')
            color = Colors.OKGREEN if score >= 90 else Colors.CYAN if score >= 70 else Colors.PURPLE
            progress_bar = create_progress_bar(score)
            print(f"{Colors.HEADER}║{Colors.ENDC} {levels[level]}")
            print(f"{Colors.HEADER}║{Colors.ENDC} {progress_bar}")
            print(f"{Colors.HEADER}║{Colors.ENDC} {color}{score:.1f}%{Colors.ENDC} (пройден {completed_at})")
            print(f"{Colors.HEADER}║{Colors.ENDC}")

    # Показываем прогресс по модулям
    print(f"{Colors.HEADER}║{Colors.ENDC} {Colors.BOLD}{Colors.GREEN}ПРОГРЕСС ПО МОДУЛЯМ:{Colors.ENDC}")
    for module_id, module_data in TRAINING_DATA.items():
        if not isinstance(module_data, dict) or 'commands' not in module_data:
            continue
            
        module_completed = 0
        module_total = 0
        
        # Считаем прогресс по модулю
        for cmd_id, cmd_data in module_data['commands'].items():
            cmd_completed = sum(1 for task in cmd_data.get('practice', []) if task['task'] in completed_tasks)
            cmd_total = len(cmd_data.get('practice', []))
            module_completed += cmd_completed
            module_total += cmd_total
            
        if module_total > 0:
            percentage = (module_completed / module_total) * 100
            progress_bar = create_progress_bar(percentage)
            module_name = module_data.get('name', f'Модуль {module_id}')
            print(f"{Colors.HEADER}║{Colors.ENDC}")
            print(f"{Colors.HEADER}║{Colors.ENDC} {Colors.BOLD}{module_name}{Colors.ENDC}")
            print(f"{Colors.HEADER}║{Colors.ENDC} {progress_bar}")
            print(f"{Colors.HEADER}║{Colors.ENDC} Прогресс: {Colors.CYAN}{module_completed}/{module_total}{Colors.ENDC} ({Colors.YELLOW}{percentage:.1f}%{Colors.ENDC})")
            
            # Показываем прогресс по каждой команде
            for cmd_id, cmd_data in module_data['commands'].items():
                cmd_completed = sum(1 for task in cmd_data.get('practice', []) if task['task'] in completed_tasks)
                cmd_total = len(cmd_data.get('practice', []))
                if cmd_total > 0:
                    cmd_percentage = (cmd_completed / cmd_total) * 100
                    cmd_color = Colors.OKGREEN if cmd_percentage == 100 else Colors.CYAN if cmd_percentage > 50 else Colors.PURPLE
                    print(f"{Colors.HEADER}║{Colors.ENDC}   • {cmd_color}{cmd_data.get('name', f'Команда {cmd_id}')}: {cmd_completed}/{cmd_total}{Colors.ENDC}")
    
    # Показываем прогресс по сценариям
    completed_scenarios = USER_PROGRESS[CURRENT_USER].get('completed_scenarios', [])
    scenarios = TRAINING_DATA.get('scenarios', {})
    if scenarios:
        print(f"{Colors.HEADER}║{Colors.ENDC}")
        print(f"{Colors.HEADER}║{Colors.ENDC} {Colors.BOLD}{Colors.YELLOW}СЦЕНАРИИ:{Colors.ENDC}")
        total_scenarios = len(scenarios)
        completed_count = len(completed_scenarios)
        if total_scenarios > 0:
            scenario_percentage = (completed_count / total_scenarios) * 100
            progress_bar = create_progress_bar(scenario_percentage)
            print(f"{Colors.HEADER}║{Colors.ENDC} {progress_bar}")
            print(f"{Colors.HEADER}║{Colors.ENDC} Выполнено: {Colors.CYAN}{completed_count}/{total_scenarios}{Colors.ENDC} ({Colors.YELLOW}{scenario_percentage:.1f}%{Colors.ENDC})")
            
            # Показываем список пройденных сценариев
    if completed_scenarios:
        print(f"{Colors.HEADER}║{Colors.ENDC}")
        print(f"{Colors.HEADER}║{Colors.ENDC} Пройденные сценарии:")
        for scenario_id in completed_scenarios:
            if scenario_id in scenarios:
                print(f"{Colors.HEADER}║{Colors.ENDC}   {Colors.OKGREEN}✓{Colors.ENDC} {scenarios[scenario_id]['name']}")

    # Показываем достижения
    achievements = USER_PROGRESS[CURRENT_USER].get('achievements', [])
    print(f"{Colors.HEADER}║{Colors.ENDC}")
    print(f"{Colors.HEADER}║{Colors.ENDC} {Colors.BOLD}{Colors.PURPLE}ДОСТИЖЕНИЯ:{Colors.ENDC}")
    if achievements:
        for achievement_id in achievements:
            achievement = ACHIEVEMENTS.get(achievement_id)
            if achievement:
                print(f"{Colors.HEADER}║{Colors.ENDC}   {achievement['name']} - {Colors.CYAN}{achievement['description']}{Colors.ENDC}")
    else:
        print(f"{Colors.HEADER}║{Colors.ENDC}   Пока нет достижений. Продолжайте обучение!")

    # Показываем статистику сессий
    stats = USER_PROGRESS[CURRENT_USER].get('session_stats', {})
    print(f"{Colors.HEADER}║{Colors.ENDC}")
    print(f"{Colors.HEADER}║{Colors.ENDC} {Colors.BOLD}{Colors.BLUE}СТАТИСТИКА:{Colors.ENDC}")
    print(f"{Colors.HEADER}║{Colors.ENDC}   Первый вход: {Colors.CYAN}{stats.get('first_login', 'Неизвестно')}{Colors.ENDC}")
    print(f"{Colors.HEADER}║{Colors.ENDC}   Последний вход: {Colors.CYAN}{stats.get('last_login', 'Неизвестно')}{Colors.ENDC}")
    
    correct_answers = stats.get('correct_answers', 0)
    total_attempts = stats.get('total_attempts', 0)
    if total_attempts > 0:
        success_rate = (correct_answers / total_attempts) * 100
        print(f"{Colors.HEADER}║{Colors.ENDC}   Успешность: {Colors.CYAN}{success_rate:.1f}%{Colors.ENDC} ({correct_answers}/{total_attempts})")
    
    sessions = stats.get('sessions', [])
    if sessions:
        print(f"{Colors.HEADER}║{Colors.ENDC}   Количество сессий: {Colors.CYAN}{len(sessions)}{Colors.ENDC}")
        
        # Находим текущую серию дней
        dates = sorted(set(s['date'] for s in sessions))
        current_streak = 1
        for i in range(len(dates)-1, 0, -1):
            date1 = datetime.datetime.strptime(dates[i], "%Y-%m-%d")
            date2 = datetime.datetime.strptime(dates[i-1], "%Y-%m-%d")
            if (date1 - date2).days == 1:
                current_streak += 1
            else:
                break
        print(f"{Colors.HEADER}║{Colors.ENDC}   Текущая серия: {Colors.CYAN}{current_streak}{Colors.ENDC} дней")

    # Закрываем рамку
    print(f"{Colors.HEADER}║{Colors.ENDC}")
    print(f"{Colors.HEADER}╚{'═' * (len(padding)*2 + len(title))}╝{Colors.ENDC}")
    
    wait_for_enter()

def create_progress_bar(percentage, width=40):
    """Создает красивый прогресс-бар заданной ширины."""
    filled = int(width * percentage / 100)
    empty = width - filled
    
    if percentage >= 90:
        color = Colors.OKGREEN  # Светло-зеленый для высокого прогресса
    elif percentage >= 50:
        color = Colors.CYAN     # Голубой для среднего прогресса
    else:
        color = Colors.PURPLE   # Фиолетовый для начального прогресса
        
    bar = f"{color}{'◆' * filled}{Colors.ENDC}{'◇' * empty}"
    return f"[{bar}] {color}{percentage:.1f}%{Colors.ENDC}"

# --- ГЛАВНЫЙ ЦИКЛ ПРОГРАММЫ ---

def main():
    """Основная функция, запускающая программу."""
    global CURRENT_USER
    
    if TRAINING_DATA is None:
        return

    load_user_progress()
    
    clear_screen()
    CURRENT_USER = input("Введите ваше имя: ").strip()
    if not CURRENT_USER:
        CURRENT_USER = "Гость"
        
    # Инициализация или обновление профиля пользователя
    if CURRENT_USER not in USER_PROGRESS:
        USER_PROGRESS[CURRENT_USER] = {
            'completed_tasks': [],
            'test_results': {},
            'completed_scenarios': [],
            'achievements': [],
            'session_stats': {
                'first_login': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'last_login': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'total_time': 0,
                'correct_answers': 0,
                'total_attempts': 0,
                'sessions': []
            }
        }
        log_action(f"Создан новый профиль пользователя {CURRENT_USER}", "SUCCESS")
    else:
        # Обновляем статистику существующего пользователя
        stats = USER_PROGRESS[CURRENT_USER].setdefault('session_stats', {})
        stats['last_login'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        stats.setdefault('sessions', []).append({
            'date': datetime.datetime.now().strftime("%Y-%m-%d"),
            'start_time': datetime.datetime.now().strftime("%H:%M:%S")
        })
        log_action(f"С возвращением, {CURRENT_USER}!", "INFO")
    
        save_user_progress()

    log_action("Запуск тренажера.")
    while True:
        clear_screen()
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║{Colors.BOLD}           ИНТЕРАКТИВНЫЙ ТРЕНАЖЕР LINUX           {Colors.ENDC}{Colors.HEADER}║{Colors.ENDC}")
        print(f"{Colors.HEADER}║{Colors.YELLOW} Пользователь: {CURRENT_USER}{' ' * (39 - len(CURRENT_USER))}{Colors.ENDC}{Colors.HEADER}║{Colors.ENDC}")
        print(f"{Colors.HEADER}╠══════════════════════════════════════════════════╣{Colors.ENDC}")
        print(f"{Colors.HEADER}║{Colors.ENDC} {Colors.PURPLE}1. 📖 Начни с меня.{Colors.ENDC}{' ' * 35}{Colors.HEADER}║{Colors.ENDC}")
        print(f"{Colors.HEADER}║{Colors.ENDC} {Colors.CYAN}2. 📚 Учебные модули{Colors.ENDC}{' ' * 31}{Colors.HEADER}║{Colors.ENDC}")
        print(f"{Colors.HEADER}║{Colors.ENDC} {Colors.GREEN}3. 🎯 Сценарии{Colors.ENDC}{' ' * 37}{Colors.HEADER}║{Colors.ENDC}")
        print(f"{Colors.HEADER}║{Colors.ENDC} {Colors.BLUE}4. ✍️  Тестирование{Colors.ENDC}{' ' * 32}{Colors.HEADER}║{Colors.ENDC}")
        print(f"{Colors.HEADER}║{Colors.ENDC} {Colors.YELLOW}5. 📊 Мой прогресс{Colors.ENDC}{' ' * 33}{Colors.HEADER}║{Colors.ENDC}")
        print(f"{Colors.HEADER}╠══════════════════════════════════════════════════╣{Colors.ENDC}")
        print(f"{Colors.HEADER}║{Colors.ENDC} {Colors.RED}0. 🚪 Выход и отправка отчета{Colors.ENDC}{' ' * 23}{Colors.HEADER}║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════╝{Colors.ENDC}")

        mode_choice = input("Выберите режим: ")
        if mode_choice == '1':
            show_guidance()
        elif mode_choice == '2':
            while True:
                clear_screen()
                print(f"\n{Colors.HEADER}╔══════════════════════════════════════╗{Colors.ENDC}")
                print(f"{Colors.HEADER}║{Colors.BOLD}      ВЫБЕРИТЕ УЧЕБНЫЙ МОДУЛЬ       {Colors.ENDC}{Colors.HEADER}║{Colors.ENDC}")
                print(f"{Colors.HEADER}╠══════════════════════════════════════╣{Colors.ENDC}")
                
                # Показываем список модулей
                module_icons = {
                    "1": "📁",  # Навигация и файлы
                    "2": "📝",  # Просмотр и обработка текста
                    "3": "⚙️",   # Управление процессами
                    "4": "🌐",  # Сетевые утилиты
                    "5": "🔧"   # Работа с оборудованием
                }
                
                for module_id, module_data in TRAINING_DATA.items():
                    # Пропускаем специальные секции (tests, scenarios)
                    if not isinstance(module_data, dict) or 'commands' not in module_data:
                        continue
                    icon = module_icons.get(str(module_id), "•")
                    print(f"{Colors.HEADER}║{Colors.ENDC} {Colors.YELLOW}{module_id}{Colors.ENDC}. {icon} {Colors.CYAN}{module_data.get('name', f'Модуль {module_id}')}{Colors.ENDC}")
                
                print(f"{Colors.HEADER}╠══════════════════════════════════════╣{Colors.ENDC}")
                print(f"{Colors.HEADER}║{Colors.ENDC} {Colors.RED}0. ⬅️  Назад{Colors.ENDC}")
                print(f"{Colors.HEADER}╚══════════════════════════════════════╝{Colors.ENDC}")
                
                module_choice = input("\nВыберите модуль: ")
                if module_choice == '0':
                    break
                    
                if module_choice in TRAINING_DATA and isinstance(TRAINING_DATA[module_choice], dict) and 'commands' in TRAINING_DATA[module_choice]:
                    # Показываем команды выбранного модуля
                    while True:
                        clear_screen()
                        module_name = TRAINING_DATA[module_choice].get('name', f'Модуль {module_choice}')
                        print(f"\n{Colors.HEADER}╔{'═' * (len(module_name) + 8)}╗{Colors.ENDC}")
                        print(f"{Colors.HEADER}║   {Colors.BOLD}{module_name}{Colors.ENDC}{Colors.HEADER}   ║{Colors.ENDC}")
                        print(f"{Colors.HEADER}╠{'═' * (len(module_name) + 8)}╣{Colors.ENDC}")
                        
                        commands = TRAINING_DATA[module_choice]['commands']
                        for cmd_id, cmd_data in commands.items():
                            name = cmd_data.get('name', f'Команда {cmd_id}')
                            if ' - ' in name:
                                command_name = name.split(' - ')[0]
                                description = name.split(' - ')[1]
                            else:
                                command_name = name
                                description = ''
                            
                            # Добавляем иконку в зависимости от типа команды
                            if 'file' in command_name.lower() or 'dir' in command_name.lower():
                                icon = "📁"
                            elif 'process' in command_name.lower() or 'kill' in command_name.lower():
                                icon = "⚙️"
                            elif 'net' in command_name.lower() or 'ssh' in command_name.lower():
                                icon = "🌐"
                            elif 'dev' in command_name.lower() or 'usb' in command_name.lower():
                                icon = "🔧"
                            else:
                                icon = "💻"
                            
                            # Определяем сложность команды по практическим заданиям
                            practice_tasks = cmd_data.get('practice', [])
                            if practice_tasks:
                                max_difficulty = max(task.get('difficulty', 1) for task in practice_tasks)
                                difficulty_color = Colors.GREEN if max_difficulty <= 2 else Colors.YELLOW if max_difficulty <= 3 else Colors.RED
                                difficulty_stars = '★' * max_difficulty
                            else:
                                difficulty_color = Colors.GREEN
                                difficulty_stars = '★'

                            # Форматируем вывод команды
                            print(f"{Colors.HEADER}║{Colors.ENDC} {Colors.BOLD}{Colors.YELLOW}{cmd_id}{Colors.ENDC}. {icon} {Colors.CYAN}{command_name}{Colors.ENDC} {difficulty_color}{difficulty_stars}{Colors.ENDC}")
                            
                            # Добавляем краткое описание с отступом
                            if description:
                                print(f"{Colors.HEADER}║{Colors.ENDC}    {Colors.PURPLE}└─ {description}{Colors.ENDC}")
                            
                            # Добавляем количество практических заданий
                            if practice_tasks:
                                print(f"{Colors.HEADER}║{Colors.ENDC}    {Colors.BLUE}└─ {len(practice_tasks)} практических заданий{Colors.ENDC}")
                        
                        print(f"{Colors.HEADER}╠{'═' * (len(module_name) + 8)}╣{Colors.ENDC}")
                        print(f"{Colors.HEADER}║{Colors.ENDC} {Colors.RED}0. ⬅️  Назад{Colors.ENDC}")
                        print(f"{Colors.HEADER}╚{'═' * (len(module_name) + 8)}╝{Colors.ENDC}")
                        
                        cmd_choice = input("\nВыберите команду: ")
                        if cmd_choice == '0':
                            break
                            
                        if cmd_choice in commands:
                            command_data = commands[cmd_choice]
                            
                            while True:
                                clear_screen()
                                # Создаем красивую рамку с заголовком
                                title = f" {command_data['name']} "
                                padding = "═" * ((50 - len(title)) // 2)
                                print(f"{Colors.HEADER}╔{padding}{title}{padding}╗{Colors.ENDC}")
                                print(f"{Colors.HEADER}║{' ' * (len(padding)*2 + len(title))}║{Colors.ENDC}")

                                # Выводим теорию с цветным форматированием
                                print(f"{Colors.HEADER}║{Colors.ENDC} {Colors.BOLD}{Colors.PURPLE}ТЕОРИЯ:{Colors.ENDC}")
                                theory_lines = command_data['theory'].split('\n')
                                for line in theory_lines:
                                    if line.strip():
                                        print(f"{Colors.HEADER}║{Colors.ENDC} {Colors.CYAN}{line}{Colors.ENDC}")
                                print(f"{Colors.HEADER}║{Colors.ENDC}")

                                # Выводим информацию о применении
                                print(f"{Colors.HEADER}║{Colors.ENDC} {Colors.BOLD}{Colors.YELLOW}КОГДА ИСПОЛЬЗОВАТЬ:{Colors.ENDC}")
                                usage_lines = command_data['when_useful'].split('\n')
                                for line in usage_lines:
                                    if line.strip():
                                        print(f"{Colors.HEADER}║{Colors.ENDC} {Colors.GREEN}{line}{Colors.ENDC}")
                                print(f"{Colors.HEADER}║{Colors.ENDC}")

                                # Выводим параметры
                                print(f"{Colors.HEADER}║{Colors.ENDC} {Colors.BOLD}{Colors.BLUE}ПАРАМЕТРЫ:{Colors.ENDC}")
                                params_lines = command_data['params'].split('\n')
                                for line in params_lines:
                                    if line.strip():
                                        print(f"{Colors.HEADER}║{Colors.ENDC} {Colors.YELLOW}{line}{Colors.ENDC}")
                                print(f"{Colors.HEADER}║{Colors.ENDC}")

                                # Нижняя часть рамки с меню
                                print(f"{Colors.HEADER}╠{'═' * (len(padding)*2 + len(title))}╣{Colors.ENDC}")
                                print(f"{Colors.HEADER}║{Colors.ENDC} {Colors.GREEN}1.{Colors.ENDC} {Colors.BOLD}Практика{Colors.ENDC}")
                                print(f"{Colors.HEADER}║{Colors.ENDC} {Colors.RED}0.{Colors.ENDC} {Colors.BOLD}Назад{Colors.ENDC}")
                                print(f"{Colors.HEADER}╚{'═' * (len(padding)*2 + len(title))}╝{Colors.ENDC}")
                                
                                action_choice = input("\nВыберите действие: ")
                                if action_choice == '0':
                                    break
                                elif action_choice == '1':
                                    run_practice_session(command_data)
                                else:
                                    print("\nНеверный выбор.")
                                    wait_for_enter()
                        else:
                            print("\nНеверный выбор команды.")
                            wait_for_enter()
                else:
                    print("\nНеверный выбор модуля.")
                    wait_for_enter()
        elif mode_choice == '3':
            run_scenario_session()
        elif mode_choice == '4':
            run_test_session()
        elif mode_choice == '5':
            show_user_progress()
        elif mode_choice == '0':
            log_action("Пользователь выбрал выход.")
            break
        else:
            print("\nНеверный выбор.")
            wait_for_enter()

    print("\nЗавершение сессии...")
    log_action("Сессия завершена.")
    send_report_email()
    print("До свидания!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nПрограмма прервана пользователем.")
        log_action("Программа принудительно прервана (Ctrl+C).")
        send_report_email()
        print("До свидания!")