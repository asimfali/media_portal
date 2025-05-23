import os
import fnmatch


def load_patterns(ignore_file='.collectignore'):
    if not os.path.exists(ignore_file):
        return []
    patterns = []
    with open(ignore_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                # Сохраняем паттерн как пару (pattern, is_include)
                # is_include=True для паттернов начинающихся с !
                is_include = line.startswith('!')
                pattern = line[1:] if is_include else line
                patterns.append((pattern, is_include))
    return patterns


def should_ignore(path, patterns):
    # Последний применимый паттерн определяет, будет ли файл игнорирован
    should_be_ignored = False  # По умолчанию включаем только явно указанные файлы

    for pattern, is_include in patterns:
        # Если паттерн — это точный путь к файлу или папке
        if pattern == path:
            should_be_ignored = not is_include
        # Если паттерн содержит wildcards (*, ? и т.д.)
        elif fnmatch.fnmatch(path, pattern):
            should_be_ignored = not is_include

    return should_be_ignored


def collect_django_modules(start_path='.', ignore_file='.collectignore'):
    output_file = 'collected_django_modules.txt'
    allowed_extensions = ('.py', '.css', '.js', '.html', '.scss')
    patterns = load_patterns(ignore_file)

    with open(output_file, 'w', encoding='utf-8') as outfile:
        for root, dirs, files in os.walk(start_path):
            # Фильтруем директории
            dirs[:] = [d for d in dirs if not should_ignore(os.path.join(root, d), patterns)]
            for file in files:
                if file.endswith(allowed_extensions):
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, start_path)
                    if should_ignore(relative_path, patterns):
                        continue
                    outfile.write(f'#{relative_path}\n')
                    try:
                        with open(file_path, 'r', encoding='utf-8') as infile:
                            outfile.write(infile.read())
                    except UnicodeDecodeError:
                        outfile.write(f"Ошибка: Не удалось прочитать {relative_path} из-за проблем с кодировкой.\n")
                    outfile.write('\n\n')  # Дополнительный отступ

    print(f"Все модули Django собраны в {output_file}")


if __name__ == "__main__":
    collect_django_modules()