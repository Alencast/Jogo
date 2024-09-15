import pygame

pygame.init()

#Variáveis da música
pygame.mixer.music.load('song/Undertale - Megalovania (1).mp3') #endereço da música
pygame.mixer.music.play(-1) #-1 para tocar em looping

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
jogador = pygame.Rect((tela_width // 2 - 50, tela_height - 100, 100, 100))
nave_inimiga = pygame.Rect((tela_width // 2 - 500, -100, 1000, 600))

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

# VARIÁVEL DE VITÓRIA
vitoria = False

# VARIÁVEL DE TAMANHO MÍNIMO
tamanho_minimo = 10  # Tamanho mínimo menor para aumentar a dificuldade

# VARIÁVEL DE REDUÇÃO DA HITBOX
reduzir_hitbox = 0.95  #  reduz 5% do tamanho original a cada hit que a nave inimiga leva
escala_hitbox = 0.8 #deixei a hitbox menor que a imagem

# CLOCK PARA CONTROLAR O FPS/ tentativa de controlar o lag
clock = pygame.time.Clock()

# Tempo entre os tiros
tempo_entre_tiros = 1000
ultimo_tiro = pygame.time.get_ticks()

# Suavização do movimento do jogador
suavizacao = 0.1  # 0.1 representa uma suavização lenta

# HITBOX DA PARTE INFERIOR DA NAVE INIMIGA
def get_hitbox_inferior_nave_inimiga():
    altura_inferior = nave_inimiga.height // 4  # A hitbox inferior será 1/4 da altura da nave
    return pygame.Rect(nave_inimiga.left, nave_inimiga.bottom - altura_inferior, nave_inimiga.width, altura_inferior)

# FUNÇÃO PARA REDIMENSIONAR A NAVE E A HITBOX CONFORME ELA FOR REDUZIAD
def redimensionar_nave(): #variavel global funciona fora do escopo da func
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
    nave_inimiga.topleft = (nave_inimiga.left + (largura - hitbox_largura) // 2, nave_inimiga.top + (altura - hitbox_altura) // 2)  # Ajusta a hitbox para ficar centralizada

    # Aumentar a velocidade conforme o tamanho da nave diminui
    fator_aumento = (1000 - nave_inimiga.width) / 1000
    velocidade_nave_inimiga = 500 + fator_aumento * 1000

# Iniciar as imagens redimensionadas
redimensionar_nave()

# GAME LOOP
run = True

while run:
    controle_fps = clock.tick(60) / 1000.0 #ajusta o fps de acordo com o desempenho do pc

    # Eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT or pygame.key.get_pressed()[pygame.K_ESCAPE]:
            run = False

    # Desenhar a imagem de fundo
    tela.blit(imagem_fundo, (0, 0))

    if vitoria:
        fonte = pygame.font.Font(None, 74)
        texto = fonte.render('VOCÊ GANHOU!', True, (0, 255, 0))
        texto_rect = texto.get_rect(center=(tela_width // 2, tela_height // 2))
        tela.fill((0, 0, 0))
        tela.blit(texto, texto_rect)
    else:
        # Movimento da nave inimiga
        nave_inimiga.x += direcao_nave_inimiga * velocidade_nave_inimiga * controle_fps

        # Verificar colisão com as bordas e ajustar a direção, +/-200 adicionado pra garantirque a nave inimiga chegue até a borda do cenário
        if nave_inimiga.right >= tela_width + 200:
            direcao_nave_inimiga = -1
        elif nave_inimiga.left <= -200:
            direcao_nave_inimiga = 1

        # Verificar colisão dos projéteis com a hitbox inferior da nave inimiga
        hitbox_inferior_nave_inimiga = get_hitbox_inferior_nave_inimiga()
        for projetil in projeteis[:]:  # itera sobre a cópia da lista projeteis, iterar sobre a lista original estava apresentando bugs
            if projetil.colliderect(hitbox_inferior_nave_inimiga):
                projeteis.remove(projetil)
                atingida = True
                tempo_atingida = pygame.time.get_ticks()
                nave_inimiga.width = max(tamanho_minimo, int(nave_inimiga.width * reduzir_hitbox))
                nave_inimiga.height = max(tamanho_minimo, int(nave_inimiga.height * reduzir_hitbox))
                redimensionar_nave()
                if nave_inimiga.width <= tamanho_minimo and nave_inimiga.height <= tamanho_minimo: #Condicional de vitória
                    vitoria = True
                break

        # Alterar a imagem da nave inimiga quando ela for atingida ou mudar a direção
        if atingida:
            if pygame.time.get_ticks() - tempo_atingida <= duracao_atingida:
                tela.blit(imagem_nave_inimiga_atingida, nave_inimiga.topleft)
            else:
                atingida = False
                tempo_atingida = 0
        else:
            if direcao_nave_inimiga > 0:
                tela.blit(imagem_nave_inimiga_direita, nave_inimiga.topleft)
            else:
                tela.blit(imagem_nave_inimiga_esquerda, nave_inimiga.topleft)

        # Movimento do jogadr com o mouse
        pos_mouse = pygame.mouse.get_pos()
        jogador.centerx += (pos_mouse[0] - jogador.centerx) * suavizacao
        
        # Evitar que a nave do jogador saia da tela
        if jogador.left < 0:
            jogador.left = 0
        if jogador.right > tela_width:
            jogador.right = tela_width
        if jogador.top < 0:
            jogador.top = 0
        if jogador.bottom > tela_height:
            jogador.bottom = tela_height

        # Eventlistener para verificar se o botão esquerdo do mouse foi pressionado para atirar
        agora = pygame.time.get_ticks()
        if pygame.mouse.get_pressed()[0] and agora - ultimo_tiro >= tempo_entre_tiros:
            projetil = pygame.Rect(jogador.centerx - 20, jogador.top, 40, 40)
            projeteis.append(projetil)
            ultimo_tiro = agora

        # Movimento dos projéteis
        for projetil in projeteis[:]:
            projetil.move_ip(0, projetil_velocidade * controle_fps)
            if projetil.bottom < 0:
                projeteis.remove(projetil)

        # Desenhar os projéteis
        for projetil in projeteis:
            tela.blit(imagem_laser, projetil.topleft)

        # Desenhar a nave do jogador
        tela.blit(imagem_nave_original, jogador.topleft)

    pygame.display.update() #Atualiza a tela (lembrar que posso atualizar apenas uma região especifica da tela, passando as coordenadas pygame.display.update((x, y, largura, altura)))

pygame.quit() #Encerra o jogo quando o programa sair do loop
