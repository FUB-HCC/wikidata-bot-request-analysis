def print_df(df, columns, width):

    header_format_str = '|'
    line_format_str = '|'
    body_format_str = '|'

    for index in range(len(columns)):
        header_format_str += '{:^' + width[index] + '}|'
        line_format_str += '{:_^' + width[index] + '}|'
        body_format_str += '{:^' + width[index] + '}|'

    print(header_format_str.format(*columns))
    print(line_format_str.format(*['' for _ in range(len(columns))]))
    for index, row in df.iterrows():
        print(body_format_str.format(*[row[column] for column in columns]))


def print_names_and_count(data, title, join_str=', '):

    print(
        "#################### Number of ", title,  ": ####################\n",
        len(data), "\n")

    print(
        "#################### ", title.capitalize(), ": ####################\n",
        join_str.join(data), "\n")
