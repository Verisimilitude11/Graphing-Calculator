import math

# Tokenizer
letters = set(list("abcdefghijklmnopqrstuvwxyz"))
numbers = set(list("0123456789."))

LPAREN = 1
RPAREN = 2
LCURLY = 3
RCURLY = 4
NUMBER = 0
IDENT = 6
OPERATOR = 7

class Token:
  def __init__(self, type, value):
    self.type = type
    self.value = value
  
  def __repr__(self):
    return "Token(%s, %s)" % (self.type, self.value)

def tokenize(code):
  tokens = []
  while len(code) > 0:
    char = code[0]
    if char == "(":
      tokens.append(Token(LPAREN, "("))
      code = code[1:]
    elif char == ")":
      tokens.append(Token(RPAREN, ")"))
      code = code[1:]
    elif char == "{":
      tokens.append(Token(LCURLY, "{"))
      code = code[1:]
    elif char == "}":
      tokens.append(Token(RCURLY, "}"))
      code = code[1:]
    elif char == "+":
      tokens.append(Token(OPERATOR, "+"))
      code = code[1:]
    elif char == "-":
      tokens.append(Token(OPERATOR, "-"))
      code = code[1:]
    elif char == "*":
      tokens.append(Token(OPERATOR, "*"))
      code = code[1:]
    elif char == "/":
      tokens.append(Token(OPERATOR, "/"))
      code = code[1:]
    elif char == "=":
      tokens.append(Token(OPERATOR, "="))
      code = code[1:]
    elif char == "^":
      tokens.append(Token(OPERATOR, "^"))
      code = code[1:]
    elif char == " ":
      code = code[1:]
    elif char in letters:
      ident, code = get_ident(code)
      tokens.append(Token(IDENT, ident))
    elif char in numbers:
      (num, code) = get_num(code)
      tokens.append(Token(NUMBER, num))
    else:
      raise SyntaxError("unknown character: " + char)

  return tokens

def get_ident(code):
  out = ""
  while (code[0]) in letters:
    out += code[0]
    code = code[1:]
    if len(code) == 0:
      return (out, code)
  return (out, code)

def get_num(code):
  out = ""
  while (code[0]) in numbers:
    out += code[0]
    code = code[1:]
    if len(code) == 0:
      return (out, code)
  return (out, code)

# Parser
NUMBER = 0
VARIABLE = 2
EXPR = 3
CALL = 4

class Node:
  def __init__(self, type, value):
    self.type = type
    self.value = value

  def __repr__(self):
    return "Node(%s, %s)" % (self.type, self.value)

def parse(tokens):
  tok = tokens[0]
  if tok.type == IDENT:
    return tokens[1:], Node(VARIABLE, tok.value)

  elif tok.type == NUMBER:
    return tokens[1:], Node(NUMBER, float(tok.value))

  elif tok.type == LPAREN:
    (tokens, val) = parse(tokens[1:])
    tok = tokens[0]
    while tok.type != RPAREN:
      op = tok.value
      (tokens, right) = parse(tokens[1:])
      val = Node(EXPR, (op, val, right))
      tok = tokens[0]
    return tokens[1:], val

  elif tok.type == LCURLY:
    tokens = tokens[1:]
    fn_name = tokens[0].value
    tokens = tokens[1:]
    params = []
    while tokens[0].type != RCURLY:
      (tokens, param) = parse(tokens)
      params.append(param)
    tokens = tokens[1:]
    return (tokens, Node(CALL, (fn_name, params)))

  raise SyntaxError("unexpected token: " + str(tok))

# Functions
functions = {
  "sqrt": lambda inp: math.sqrt(inp[0]),
  "sin": lambda inp: math.sin(inp[0]),
  "cos": lambda inp: math.cos(inp[0]),
  "tan": lambda inp: math.tan(inp[0]),
  "fact": lambda inp: math.gamma(inp[0]) * inp[0],
}

# Evaluator
def eval_node(node, variables):
  if node.type == NUMBER:
    return node.value
  elif node.type == VARIABLE:
    return variables[node.value]
  elif node.type == EXPR:
    (op, left, right) = node.value
    left = eval_node(left, variables)
    right = eval_node(right, variables)
    if op == "+":
      return left + right
    elif op == "-":
      return left - right
    elif op == "*":
      return left * right
    elif op == "/":
      return left / right
    elif op == "^":
      return left ** right
    else:
      raise SyntaxError("unknown operator: " + op)
  elif node.type == CALL:
    (fn_name, params) = node.value
    if fn_name in functions:
      return functions[fn_name]([eval_node(param, variables) for param in params])
    else:
      raise NameError("unknown function: " + fn_name)
  else:
    raise ValueError("unknown node: " + str(node))

# Parse
src = input("Enter an equation (must be in parenthesis): ")
(_, eq) = parse(tokenize(src))

# Graph
import pygame
import pygame.freetype
pygame.init()
font = pygame.freetype.Font(input("font: "), 12)
font.fgcolor = (0, 0, 0)

WIDTH = 800
HEIGHT = 800
win = pygame.display.set_mode((WIDTH, HEIGHT))

scale = WIDTH / 20 # Scale so that its 20 units wide (-10, -10)
offx = WIDTH / 2 # Centered
offy = HEIGHT / 2 # Centered

def coord_to_screen(x, y):
  # Flip y
  y = -y

  # Scale
  x = x * scale
  y = y * scale

  # Offset
  x += offx
  y += offy

  return (x, y)

def screenx_to_coord(x):
  return (x - offx) / scale # Opposite of above steps for x

def screeny_to_coord(y):
  return -((y - offy) / scale) # Opposite of above steps for y

# Draw func
def draw():
  win.fill((255, 255, 255))

  # Draw axes
  pygame.draw.line(win, (0, 0, 0), (0, offy), (WIDTH, offy), width=2)
  pygame.draw.line(win, (0, 0, 0), (offx, 0), (offx, HEIGHT), width=2)

  offamount = 10

  # X-Axis
  numticks = int(WIDTH / scale)
  incr = math.floor(numticks / 20) # 20 ticks at once
  if incr < 1:
    incr = 1
  left = math.ceil(screenx_to_coord(0))
  for i in range(int(left), int(left + numticks + 1), int(incr)):
    x = i
    y = 0
    (x, y) = coord_to_screen(x, y)
    pygame.draw.line(win, (0, 0, 0), (x, y - offamount), (x, y + offamount), width=1)
    txt = str(int(i))
    rect = font.get_rect(txt)
    font.render_to(win, (x - rect.width / 2, offy - offamount * 2 - 10), txt) # get_width instead of 12

  # Y-Axis
  numticks = int(HEIGHT / scale)
  incr = math.floor(numticks / 20) # 20 ticks at once
  if incr < 1:
    incr = 1
  top = math.floor(screeny_to_coord(HEIGHT))
  for i in range(int(top), int(top + numticks + 1), int(incr)):
    x = 0
    y = i
    (x, y) = coord_to_screen(x, y)
    pygame.draw.line(win, (0, 0, 0), (x - offamount, y), (x + offamount, y), width=1)
    txt = str(int(i))
    rect = font.get_rect(txt)
    font.render_to(win, (offx - offamount * 2 - 10, y - rect.height / 2), txt) # get_height instead of 12

  # Draw function
  prevxv = 0
  prevyv = 0
  noprev = True
  for x in range(0, WIDTH):
    xv = screenx_to_coord(x)
    try:
      yv = eval_node(eq, {"x": xv})
    except (ZeroDivisionError, ValueError):
      noprev = True
      continue
    
    if noprev:
      prevxv = xv
      prevyv = yv
      noprev = False
    else:
      (x, y) = coord_to_screen(xv, yv) # Pixel by pixel eval func
      (prevx, prevy) = coord_to_screen(prevxv, prevyv) # Pixel by pixel eval func
      pygame.draw.line(win, (255, 0, 0), (prevx, prevy), (x, y), width=2)
      prevxv = xv
      prevyv = yv

  pygame.display.flip()

# Main loop
running = True
draw()
while running:
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      running = False
  
  keys = pygame.key.get_pressed()
  changed = False

  speed = 3
  speedscale = 1.01
  if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
    speed = 6
    speedscale = 1.1

  if keys[pygame.K_LEFT]:
    offx += speed
    changed = True
  if keys[pygame.K_RIGHT]:
    offx -= speed
    changed = True
  if keys[pygame.K_UP]:
    offy += speed
    changed = True
  if keys[pygame.K_DOWN]:
    offy -= speed
    changed = True
  if keys[pygame.K_EQUALS]: # Plus
    scale *= speedscale
    changed = True
  if keys[pygame.K_MINUS]: # Minus
    scale /= speedscale
    changed = True

  # Shortcuts
  if keys[pygame.K_h]:
    # Home
    scale = WIDTH / 20
    offx = WIDTH / 2
    offy = HEIGHT / 2
    draw()
  
  if changed:
    draw()
