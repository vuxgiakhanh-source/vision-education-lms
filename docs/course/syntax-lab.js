/* Tiny, bounded teaching language. No eval/Function/HTTP/DOM execution. */
(function (root) {
  'use strict';
  const format = value => typeof value === 'string' ? JSON.stringify(value) : String(value);
  function run(source) {
    const output = [], trace = [], variables = new Map();
    let tokens = [], position = 0;
    function fail(message, token) {
      const error = new Error(message);
      error.line = token?.line || 1;
      throw error;
    }
    try {
      if (source.length > 4000) fail('Giữ bài tập dưới 4000 ký tự.');
      let index = 0, line = 1;
      while (index < source.length) {
        const c = source[index];
        if (/\s/.test(c)) { if (c === '\n') line++; index++; continue; }
        if (source.slice(index, index + 2) === '//') {
          while (index < source.length && source[index] !== '\n') index++;
          continue;
        }
        if (c === '"' || c === "'") {
          const quote = c, startLine = line;
          let value = '', closed = false; index++;
          while (index < source.length) {
            const next = source[index++];
            if (next === quote) { closed = true; break; }
            if (next === '\n' || next === '\r') fail('Chuỗi cần dấu nháy đóng trước khi xuống dòng.', { line: startLine });
            if (next === '\\') {
              const escaped = source[index++];
              const escapes = { n: '\n', r: '\r', t: '\t', '\\': '\\', '"': '"', "'": "'" };
              if (!Object.hasOwn(escapes, escaped)) fail('Bộ luyện chưa hỗ trợ escape này.', { line });
              value += escapes[escaped];
            } else value += next;
          }
          if (!closed) fail('Thiếu dấu nháy đóng chuỗi.', { line: startLine });
          tokens.push({ kind: 'literal', value, line }); continue;
        }
        const number = source.slice(index).match(/^\d+(?:\.\d+)?/);
        if (number) { tokens.push({ kind: 'literal', value: Number(number[0]), line }); index += number[0].length; continue; }
        const name = source.slice(index).match(/^[A-Za-z_$][A-Za-z0-9_$]*/);
        if (name) { tokens.push({ kind: 'name', value: name[0], line }); index += name[0].length; continue; }
        const operator = ['===', '!==', '>=', '<=', '=', '+', '-', '*', '/', '>', '<', '(', ')', ';', '.'].find(value => source.startsWith(value, index));
        if (!operator) fail(`Bộ luyện chưa hỗ trợ ký hiệu ${c}. Nó chỉ chạy biến, phép tính, so sánh và console.log.`, { line });
        tokens.push({ kind: 'symbol', value: operator, line }); index += operator.length;
      }
      tokens.push({ kind: 'end', value: '', line });
      const current = () => tokens[position];
      const matches = value => current().kind !== 'literal' && current().value === value;
      const take = value => {
        const token = current();
        if (!matches(value)) fail(`Cần ${value} tại đây.`, token);
        position++; return token;
      };
      const identifier = () => {
        const token = current();
        if (token.kind !== 'name' || ['let', 'const', 'true', 'false', 'console', 'if', 'for', 'function', 'return'].includes(token.value)) fail('Cần tên biến như diem hoặc soBai; tên không đặt trong dấu nháy.', token);
        position++; return token;
      };
      const precedence = { '===': 1, '!==': 1, '>': 2, '<': 2, '>=': 2, '<=': 2, '+': 3, '-': 3, '*': 4, '/': 4 };
      function expression(minimum = 0, depth = 0) {
        if (depth > 40) fail('Ngoặc lồng quá nhiều cho bài luyện này.', current());
        const token = current(); let left;
        if (token.kind === 'literal') { position++; left = { kind: 'value', value: token.value, token }; }
        else if (matches('true') || matches('false')) { position++; left = { kind: 'value', value: token.value === 'true', token }; }
        else if (matches('-')) { position++; left = { kind: 'negative', value: expression(5, depth + 1), token }; }
        else if (matches('(')) { position++; left = expression(0, depth + 1); take(')'); }
        else { left = { kind: 'read', token: identifier() }; }
        while (current().kind === 'symbol' && Object.hasOwn(precedence, current().value) && precedence[current().value] >= minimum) {
          const operation = current(); position++;
          left = { kind: 'binary', left, right: expression(precedence[operation.value] + 1, depth + 1), token: operation };
        }
        return left;
      }
      const program = [], declared = new Set();
      while (current().kind !== 'end') {
        if (program.length >= 100) fail('Tối đa 100 câu lệnh trong một bài luyện.', current());
        const start = current(); let statement;
        if (matches('let') || matches('const')) {
          position++; const name = identifier();
          if (declared.has(name.value)) fail(`Tên ${name.value} đã được khai báo trong lần chạy này.`, name);
          declared.add(name.value); take('=');
          statement = { kind: 'declare', name, mutable: start.value === 'let', value: expression(), token: start };
        } else if (matches('console')) {
          take('console'); take('.'); take('log'); take('(');
          statement = { kind: 'print', value: expression(), token: start }; take(')');
        } else {
          const name = identifier(); take('=');
          statement = { kind: 'assign', name, value: expression(), token: start };
        }
        take(';'); program.push(statement);
      }
      function value(node) {
        if (node.kind === 'value') return node.value;
        if (node.kind === 'read') {
          if (!variables.has(node.token.value)) fail(`Chưa khai báo biến ${node.token.value}. Thử let ${node.token.value} = 0; trước khi đọc.`, node.token);
          return variables.get(node.token.value).value;
        }
        if (node.kind === 'negative') return -value(node.value);
        const left = value(node.left), right = value(node.right);
        switch (node.token.value) {
          case '+': return left + right;
          case '-': return left - right;
          case '*': return left * right;
          case '/': return left / right;
          case '===': return left === right;
          case '!==': return left !== right;
          case '>': return left > right;
          case '<': return left < right;
          case '>=': return left >= right;
          case '<=': return left <= right;
          default: throw new Error('Unsupported operation');
        }
      }
      for (const statement of program) {
        const result = value(statement.value);
        let action;
        if (statement.kind === 'print') { output.push(String(result)); action = `Hiển thị ${format(result)}; các biến không đổi.`; }
        else if (statement.kind === 'declare') {
          if (variables.has(statement.name.value)) fail(`Tên ${statement.name.value} đã được khai báo trong lần chạy này.`, statement.name);
          variables.set(statement.name.value, { value: result, mutable: statement.mutable });
          action = `Tạo biến ${statement.name.value} và gắn giá trị ${format(result)}.`;
        } else {
          const previous = variables.get(statement.name.value);
          if (!previous) fail(`Chưa khai báo biến ${statement.name.value}.`, statement.name);
          if (!previous.mutable) fail(`${statement.name.value} được khai báo bằng const nên không được gán lại. Dùng let khi cần đổi giá trị.`, statement.name);
          previous.value = result;
          action = `Tính vế phải trước, rồi đổi ${statement.name.value} thành ${format(result)}.`;
        }
        trace.push({ line: statement.token.line, action,
          variables: Object.fromEntries([...variables].map(([name, item]) => [name, item.value])) });
      }
      return { ok: true, output, trace };
    } catch (error) {
      return { ok: false, output, trace, error: error.message, line: error.line || 1 };
    }
  }
  const api = { run, format };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else root.SyntaxLab = api;
})(typeof window !== 'undefined' ? window : globalThis);
