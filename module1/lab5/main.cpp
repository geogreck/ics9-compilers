#include <vector>
#include <fstream>
#include <iostream>
#include <memory>

#include "lexer.hpp"

#include <FlexLexer.h>

int main(int argc, char const *argv[])
{
    if (argc != 2)
    {
        std::cout << "filename must be passed" << std::endl;
        return 1;
    }

    std::ifstream file(argv[1]);
    if (!file.is_open())
    {
        std::cout << "failed to open file "<< std::endl;
        return 1;
    }


    std::vector<std::unique_ptr<Token>> tokens;
    TokenDomain domain;
    Attribute attr;
    Fragment coords;

    std::shared_ptr<Compiler> compiler = std::make_shared<Compiler>();
    Scanner scanner = Scanner(compiler, file);

    while (domain != TokenDomain::END_OF_PROGRAM)
    {
        domain = scanner.lex(attr, coords);

        auto fixed_coords = Fragment(coords.starting, Position(coords.following.line, coords.following.pos - 1, 0));

        switch (domain)
        {
        case TokenDomain::INT:
        {
            int64_t &value = std::get<int64_t>(attr);
            tokens.push_back(std::make_unique<IntToken>(fixed_coords, value));
            break;
        }
        case TokenDomain::IDENT:
        {
            int64_t &value = std::get<int64_t>(attr);
            tokens.push_back(std::make_unique<IdentToken>(fixed_coords, value));
            break;
        }
        case TokenDomain::STRING:
        {
            std::string &value = std::get<std::string>(attr);
            tokens.push_back(std::make_unique<StringToken>(fixed_coords, value));
        }
        }
    }

    for (const auto &token : tokens)
    {
        std::cout << *token << std::endl;
    }

    std::cout << "messages: ";
    for (const auto &[position, message] : compiler->messages)
    {
        std::cout << "( " << position << " " << message << " )";
    }
    std::cout << std::endl;

    return 0;
}
