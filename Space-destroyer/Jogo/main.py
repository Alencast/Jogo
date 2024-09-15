import pygame

pygame.init()

# Variáveis da música
pygame.mixer.music.load('song/Undertale - Megalovania (1).mp3')  # Endereço da música
pygame.mixer.music.play(-1)  # -1 para tocar em looping

# PEGAR A RESOLUÇÃO MÁXIMA DO MONITOR DE FORMA DINÂMICA
info = pygame.display.Info()
tela_width = info.current_w
tela_height = info.current_h

# WINDOW
tela = pygame.display.set_mode((tela_width, tela_height), pygame.FULLSCREEN)

# CARREGAR IMAGEM DE FUNDO
imagem_fundo = pygame.image.load('img/espaço.png')
imagem_fundo = pygame.transform.scale(imagem_fundo, (tela_width, tela_height))

# CARREGAR IMAGEM DA NAVE DO JOGADOR
imagem_nave_original = pygame.image.load('img/nave.png')
imagem_nave_original = pygame.transform.scale(imagem_nave_original, (100, 100))

# CARREGAR IMAGENS DA NAVE INIMIGA
imagem_nave_inimiga_esquerda_original = pygame.image.load('img/nave_inimiga_esquerda.png')
imagem_nave_inimiga_direita_original = pygame.image.load('img/nave_inimiga_direita.png')
imagem_nave_inimiga_atingida_original = pygame.image.load('img/nave_inimiga_hit-removebg-preview.png')

# CARREGAR IMAGEM DO LASER
imagem_laser = pygame.image.load('img/laser.png')
imagem_laser = pygame.transform.scale(imagem_laser, (40, 40))

# Nave inimiga e do jogador
jogador = pygame.Rect((tela_width // 2 - 50, tela_height - 100, 100, 100)) #posição e tamanho da nave
nave_inimiga = pygame.Rect((tela_width // 2 - 500, -100, 1000, 600))#posiçai e tamanho da nave inimiga

# VARIÁVEIS DA NAVE INIMIGA
velocidade_nave_inimiga = 500
direcao_nave_inimiga = 1

# VARIÁVEIS DO TIRO
projetil_velocidade = -1000
projeteis = []

# VARIÁVEIS DE ATINGIMENTO
atingida = False
tempo_atingida = 0
duracao_atingida = 1000

# VARIÁVEL DE VITÓRIA E DERROTA
vitoria = False
derrota = False

# VARIÁVEL DE TAMANHO MÍNIMO
tamanho_minimo = 10  # Tamanho mínimo menor para aumentar a dificuldade

# VARIÁVEL DE REDUÇÃO DA HITBOX
reduzir_hitbox = 0.95  #  reduz 5% do tamanho original a cada hit que a nave inimiga leva
escala_hitbox = 0.8  # Deixei a hitbox menor que a imagem

# CLOCK PARA CONTROLAR O FPS
clock = pygame.time.Clock()

# Tempo entre os tiros
tempo_entre_tiros = 1000
ultimo_tiro = pygame.time.get_ticks()

# Suavização do movimento do jogador
suavizacao = 0.1  # 0.1 representa uma suavização lenta

# Tempo do relógio (1 minuto)
tempo_total = 60 * 1000  # 1 minuto em milissegundos
tempo_inicial = pygame.time.get_ticks()

# FUNÇÕES AUXILIARES

# Hitbox inferior da nave inimiga
def get_hitbox_inferior_nave_inimiga():
    altura_inferior = nave_inimiga.height // 4  # A hitbox inferior será 1/4 da altura da nave
    return pygame.Rect(nave_inimiga.left, nave_inimiga.bottom - altura_inferior, nave_inimiga.width, altura_inferior)

# Redimensionar a nave inimiga
def redimensionar_nave():
    global imagem_nave_inimiga_esquerda, imagem_nave_inimiga_direita, imagem_nave_inimiga_atingida, nave_inimiga, velocidade_nave_inimiga
    largura = int(nave_inimiga.width * reduzir_hitbox)
    altura = int(nave_inimiga.height * reduzir_hitbox)
    
    # Redimensionar as imagens da nave inimiga
    imagem_nave_inimiga_esquerda = pygame.transform.scale(imagem_nave_inimiga_esquerda_original, (largura, altura))
    imagem_nave_inimiga_direita = pygame.transform.scale(imagem_nave_inimiga_direita_original, (largura, altura))
    imagem_nave_inimiga_atingida = pygame.transform.scale(imagem_nave_inimiga_atingida_original, (largura, altura))
    
    # Redimensionar a hitbox para ser 80% do tamanho da imagem
    hitbox_largura = int(largura * escala_hitbox)
    hitbox_altura = int(altura * escala_hitbox)
    nave_inimiga.width = hitbox_largura
    nave_inimiga.height = hitbox_altura
    nave_inimiga.topleft = (nave_inimiga.left + (largura - hitbox_largura) // 2, nave_inimiga.top + (altura - hitbox_altura) // 2)

    # Aumentar a velocidade conforme o tamanho da nave diminui
    fator_aumento = (1000 - nave_inimiga.width) / 1000
    velocidade_nave_inimiga = 500 + fator_aumento * 1000

# Reiniciar o jogo
def reiniciar_jogo():
    global vitoria, derrota, nave_inimiga, velocidade_nave_inimiga, direcao_nave_inimiga, projeteis, atingida, tempo_atingida, tempo_inicial
    vitoria = False
    derrota = False
    nave_inimiga.width = 1000
    nave_inimiga.height = 600
    nave_inimiga.topleft = (tela_width // 2 - 500, -100)
    velocidade_nave_inimiga = 500
    direcao_nave_inimiga = 1
    projeteis = []
    atingida = False
    tempo_atingida = 0
    tempo_inicial = pygame.time.get_ticks()
    redimensionar_nave()

# Iniciar as imagens redimensionadas
redimensionar_nave()

# GAME LOOP
run = True

while run:
    controle_fps = clock.tick(60) / 1000.0

    # Eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT or pygame.key.get_pressed()[pygame.K_ESCAPE]:
            run = False

        # Verificar clique no botão "Jogar Novamente" na tela de vitória ou derrota
        if (vitoria or derrota) and event.type == pygame.MOUSEBUTTONDOWN:
            if botao_rect.collidepoint(pygame.mouse.get_pos()):
                reiniciar_jogo()

    # Desenhar a imagem de fundo
    tela.blit(imagem_fundo, (0, 0))

    # Verificar o tempo restante
    tempo_restante = tempo_total - (pygame.time.get_ticks() - tempo_inicial)
    if tempo_restante <= 0 and not vitoria:
        derrota = True

    if vitoria:
        # Desenhar o texto de vitória
        fonte = pygame.font.Font(None, 74)
        texto = fonte.render('VOCÊ GANHOU!', True, (0, 255, 0))  # anti-alising true
        texto_rect = texto.get_rect(center=(tela_width // 2, tela_height // 2 - 50))
        tela.fill((0, 0, 0))
        tela.blit(texto, texto_rect)

        # Desenhar o botão "Jogar Novamente"
        fonte_botao = pygame.font.Font(None, 50)
        botao_texto = fonte_botao.render('JOGAR NOVAMENTE', True, (0, 255, 0))  # anti-alising true
        botao_rect = botao_texto.get_rect(center=(tela_width // 2, tela_height // 2 + 50))  # centralizar o texto de jogar novamente no meio da tela
        pygame.draw.rect(tela, (255, 255, 255), botao_rect.inflate(20, 20))  # Rect azul ao redor do texto
        tela.blit(botao_texto, botao_rect)

    elif derrota:
        # Desenhar o texto de derrota
        fonte = pygame.font.Font(None, 74)
        texto = fonte.render('VOCÊ PERDEU!', True, (255, 0, 0))  # anti-alising true
        texto_rect = texto.get_rect(center=(tela_width // 2, tela_height // 2 - 50))
        tela.fill((0, 0, 0))
        tela.blit(texto, texto_rect)

        # Desenhar o botão "Jogar Novamente"
        fonte_botao = pygame.font.Font(None, 50)
        botao_texto = fonte_botao.render('JOGAR NOVAMENTE', True, (255, 0, 0))  # anti-alising true
        botao_rect = botao_texto.get_rect(center=(tela_width // 2, tela_height // 2 + 50))  # centralizar o texto de jogar novamente no meio da tela
        pygame.draw.rect(tela, (255, 255, 255), botao_rect.inflate(20, 20))  # rect azul ao redor do texto
        tela.blit(botao_texto, botao_rect)

    else:
        # Atualizar nave do jogador
        pos_mouse = pygame.mouse.get_pos()[0]
        jogador.x += (pos_mouse - jogador.centerx) * suavizacao

        # Desenhar nave do jogador
        tela.blit(imagem_nave_original, jogador)

        # Movimento da nave inimiga
        nave_inimiga.x += int(velocidade_nave_inimiga * direcao_nave_inimiga * controle_fps)
        if nave_inimiga.right >= tela_width or nave_inimiga.left <= 0:
            direcao_nave_inimiga *= -1

        # Desenhar nave inimiga
        if atingida and pygame.time.get_ticks() - tempo_atingida <= duracao_atingida:
            tela.blit(imagem_nave_inimiga_atingida, nave_inimiga.topleft)
        else:
            imagem_nave_atual = imagem_nave_inimiga_esquerda if direcao_nave_inimiga == -1 else imagem_nave_inimiga_direita
            tela.blit(imagem_nave_atual, nave_inimiga.topleft)
            atingida = False

        # Desenhar projéteis
        for projetil in projeteis:
            projetil.y += projetil_velocidade * controle_fps
            tela.blit(imagem_laser, projetil)

        # Verificar se projéteis atingem a nave inimiga
        for projetil in projeteis[:]:
            if get_hitbox_inferior_nave_inimiga().colliderect(projetil):
                atingida = True
                tempo_atingida = pygame.time.get_ticks()
                projeteis.remove(projetil)
                if nave_inimiga.width > tamanho_minimo:
                    redimensionar_nave()
                else:
                    vitoria = True

        # Remover projéteis fora da tela
        projeteis = [projetil for projetil in projeteis if projetil.bottom > 0]

        # Gerar novos projéteis
        if pygame.mouse.get_pressed()[0] and pygame.time.get_ticks() - ultimo_tiro >= tempo_entre_tiros:
            projeteis.append(pygame.Rect(jogador.centerx - 20, jogador.top - 20, 40, 40))
            ultimo_tiro = pygame.time.get_ticks()

    # contador
    fonte_tempo = pygame.font.Font(None, 50)
    minutos = tempo_restante // 60000 # tempo_restante // 60000 divide o tempo restante em milissegundos por 60k para pegar o número de minutos
    segundos = (tempo_restante % 60000) // 1000 #pega o resto da divisão por 60.000 ( o tempo abaixo de um minuto) e divide por 1000 para converter em segundos
    tempo_texto = fonte_tempo.render(f"Fim do mundo em: {minutos}:{segundos:02d}", True, (255, 255, 255))  # anti-alising true
    tela.blit(tempo_texto, (50, 50))

    # Atualizar a tela
    pygame.display.flip()

pygame.quit()
