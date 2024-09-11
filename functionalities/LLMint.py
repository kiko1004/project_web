from openai import OpenAI


def get_sql_query(request: str):
    client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")
    messages = [
        {"role": "system",
         "content": 'I have an SQL in MySQL and I want you to create SQL scripts given my instructions. The table, called "hist", has columns "date" which is varchar, "ticker" which is varchar and "close" which is float.  When you build the SQL code please specify the database ("prices") in the FROM statement. For example prices.hist. I want you to output only the SQL code in plain text! Do not include anything else in your answer! Please output only the SQL code in plain text!'},
        {"role": "user", "content": request}
    ]

    completion = client.chat.completions.create(
        model="lmstudio-community/Meta-Llama-3.1-8B-Instruct-GGUF",
        messages=messages,
        temperature=0.7,
    )

    query = completion.choices[0].message.content.replace("\n", " ").replace(";", "")
    return query


if __name__ == '__main__':
    print(get_sql_query("give me all the data for msft"))