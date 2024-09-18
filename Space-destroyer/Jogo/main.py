import pygame

pygame.init() #inicia os módulos do Pygame necessários pra rodar o game

# Variáveis da música
pygame.mixer.music.load('song/Undertale - Megalovania (1).mp3')  # Endereço da música
pygame.mixer.music.play(-1)  # -1 para tocar em looping

# PEGAR A RESOLUÇÃO MÁXIMA DO MONITOR DE FORMA DINÂMICA
info = pygame.display.Info() #Pega a resolução máxima do monitor do jogador

pygame.mouse.set_visible(False)

#Armazena a largura e a altura da tela na variável tela_width e tela_height
tela_width = info.current_w
tela_height = info.current_h

# WINDOW
tela = pygame.display.set_mode((tela_width, tela_height), pygame.FULLSCREEN) #Set mode cria a janela do jogo no modo tela cheia, com a resolução máxima do monitor

# CARREGAR IMAGEM DE FUNDO
#Carrega o background do jogo e redimensiona pra ocupar toda a tela
imagem_fundo = pygame.image.load('img/espaço.png')
imagem_fundo = pygame.transform.scale(imagem_fundo, (tela_width, tela_height))

# CARREGAR IMAGEM DA NAVE DO JOGADOR
#Carrega e redimensiona a imagem da nave do jogador para 100 por 100 px
imagem_nave_original = pygame.image.load('img/nave.png')
imagem_nave_original = pygame.transform.scale(imagem_nave_original, (100, 100))

# CARREGAR IMAGENS DA NAVE INIMIGA
#Carrega as imagens da nave inimiga (uma para a nave indo para a esquerda, uma para a direita e uma quando atingida)
imagem_nave_inimiga_esquerda_original = pygame.image.load('img/nave_inimiga_esquerda.png')
imagem_nave_inimiga_direita_original = pygame.image.load('img/nave_inimiga_direita.png')


# CARREGAR IMAGEM DO LASER
#Carrega e redimensiona a imagem do laser, 40px por 40px 
imagem_laser = pygame.image.load('img/laser.png')
imagem_laser = pygame.transform.scale(imagem_laser, (40, 40)) #width, height

# Nave inimiga e do jogador
#Cria a nave do jogador com o Rect(container) que define a posição e o tamanho (100 por 100) da nave no centro da tela, na parte inferior
#Rect define áreas retangulares para posicionamento, colisão e manipulação de objetos no jogo.
jogador = pygame.Rect((tela_width // 2 - 50, tela_height - 100, 100, 100)) #posição e tamanho da nave (x, y, width, height)
nave_inimiga = pygame.Rect((tela_width // 2 - 500, -100, 1000, 600))#posiçai e tamanho da nave inimiga (x, y, width, height)

# VARIÁVEIS DA NAVE INIMIGA
#Define a velocidade de movimentação da nave inimiga e a direção (1 significa que ela começa se movendo para a direita, -1 é pra esquerda)
velocidade_nave_inimiga = 500
direcao_nave_inimiga = 1

# VARIÁVEIS DO TIRO
#Define a velocidade dos lasers e cria uma lista pra armazenar os projéteis no jogo, isso vai ser utilizado pra controlar o tempo e "viuda útil" dos disparos
projetil_velocidade = -1000 #negativo pois o projetil está se movendo de baixo pra cima no eixo y (em ms)
projeteis = []

# VARIÁVEIS DA HITBOX
#Controla se a nave inimiga foi atingida e por quanto tempo (milissegundos) ela ficará "atingida" antes de retornar ao normal
atingida = False

duracao_atingida = 1000 # em ms


#Variávesi de vitória e derrota que serão utilizadas pra definir o status do jogo
vitoria = False
derrota = False

# VARIÁVEL DE TAMANHO MÍNIMO
tamanho_minimo = 10  # Tamanho mínimo que a nave pode chegar antes do jogo terminar

# VARIÁVEL DE REDUÇÃO DA HITBOX
reduzir_hitbox = 0.95  # multiplicar o tamanho por 0.95,  reduz 5% do tamanho original a cada hit que a nave inimiga leva
escala_hitbox = 0.8  # Deixei a hitbox menor que a imagem

# CLOCK PARA CONTROLAR O FPS
clock = pygame.time.Clock()

# Tempo entre os tiros
#Define o intervalo de 1 segundo (1000 ms) entre cada tiro e armazena o tempo do último tiro, pra limitar a quantidade de tiros a 1 por segundo
tempo_entre_tiros = 1000 #em ms
ultimo_tiro = pygame.time.get_ticks()

# Suavização do movimento do jogador
suavizacao = 0.1  # 0.1 suavização lenta

# Tempo do relógio (1 minuto)
#Define o tempo total de 60 segundos para o jogador impedir o ataque da nave inimiga e armazena o tempo inicial
tempo_total = 60 * 1000  # 1 minuto em milissegundos
tempo_inicial = pygame.time.get_ticks() # pega o tempo desde que o pygame foi iniciado, serve pra criar um temporizador e medir intervalos, nesse contexto 
# restante de jogo é utilizado pra calcular o tempo 


# FUNÇÕES AUXILIARES: redimensionar_nave e reiniciar_jogo

# Redimensionar a nave inimiga
#Reduz o tamanho da nave inimiga quando atingida, ajusta as imagens da nave, e aumenta sua velocidade à medida que o tamanho diminui
def redimensionar_nave():
    global imagem_nave_inimiga_esquerda, imagem_nave_inimiga_direita, nave_inimiga, velocidade_nave_inimiga #utilizar variáveis globais pq são constantes
    largura = int(nave_inimiga.width * reduzir_hitbox) #redimensiona a width e reduz o hitbox da nave
    altura = int(nave_inimiga.height * reduzir_hitbox) #redimensiona a height e reduz o hitbox da nave
    
    # Redimensionar as imagens da nave inimiga
    imagem_nave_inimiga_esquerda = pygame.transform.scale(imagem_nave_inimiga_esquerda_original, (largura, altura))
    imagem_nave_inimiga_direita = pygame.transform.scale(imagem_nave_inimiga_direita_original, (largura, altura))   
    
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
#Reinicia todas as variáveis do jogo (como nave inimiga, projéteis, e estado de vitória/derrota) para começar uma nova partida
def reiniciar_jogo():
    global vitoria, derrota, nave_inimiga, velocidade_nave_inimiga, direcao_nave_inimiga, projeteis, atingida, tempo_atingida, tempo_inicial #utilizar variáveis globais pq são constantes
    vitoria = False
    derrota = False
    nave_inimiga.width = 1000
    nave_inimiga.height = 600
    nave_inimiga.topleft = (tela_width // 2 - 500, -100)
    velocidade_nave_inimiga = 500
    direcao_nave_inimiga = 1
    projeteis = []
    atingida = False
   
    tempo_inicial = pygame.time.get_ticks()
    redimensionar_nave()

# Iniciar as imagens redimensionadas
redimensionar_nave()

# GAME LOOP
run = True

while run:
    #trabalhando com milisegundos para para garantir o controle e a precisão do tempo do jogo
    controle_fps = clock.tick(60) / 1000.0 # define o limite de FPS (60 frames por segundo) e calcula o tempo passado desde o último frame

    # Eventos          
    for event in pygame.event.get():#Isso itera sobre todos os eventos que ocorreram desde a última iteração do loop, pra verificar os eventos que ocorreram (tecla pressionada, click, etc)
         #verificando eventos que podem encerrar o jogo, como fechar a tela ou apertar ESC pra fechar
        if event.type == pygame.QUIT:
            run = False # caso o jogador aperte ESC ou feche a tela do jogo, o status de run passa a ser falso e o jogo encerra
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: #verifica se a tecla foi apertada e se essa tecla foi o ESC
            run = False # caso o jogador aperte ESC ou feche a tela do jogo, o status de run passa a ser falso e o jogo encerra

        # Verificar click no botão "Jogar Novamente" na tela de vitória ou derrota
        if (vitoria or derrota) and event.type == pygame.MOUSEBUTTONDOWN: #verifica o status do jogo (vitoria ou derrota) e verifica o evento de click no mouse
            if botao_rect.collidepoint(pygame.mouse.get_pos()): #verifica se o clique do mouse ocorreu dentro da área do botão "Jogar Novamente"
                reiniciar_jogo() #caso seja, a função de reiniciar o jogo vai ser chamada

    # Desenhar a imagem de fundo
    tela.blit(imagem_fundo, (0, 0)) # O blit renderiza a imagem de fundo na posição (0, 0) da tela

    # Verificar o tempo restante, caso o tempo termine o jogo encerra em derrota
    tempo_restante = tempo_total - (pygame.time.get_ticks() - tempo_inicial) # compara o tempo total, menos o que já passou, pra saber o tempo restante de jogo
    if tempo_restante <= 0 and not vitoria: # se o tempo restante for menor ou igual a 0 e o jogador ainda não tiver vencido, o jogo encerra em derrota
        derrota = True   
        
    #condicionais das telas de vitória/derrota
    if vitoria:
        # Desenhar a tela de vitória
        fonte = pygame.font.Font(None, 74) #fonte do texto
        texto = fonte.render('VOCÊ GANHOU!', True, (0, 255, 0))  # anti-alising true, renderiza a tela de vitória
        texto_rect = texto.get_rect(center=(tela_width // 2, tela_height // 2 - 50)) #cria e centraliza o rect do texto
        tela.fill((255, 255, 255)) #preenche o resto da tela com a cor branca (pra esconder o contador kk)
        tela.blit(texto, texto_rect)

        # Desenhar o botão "Jogar Novamente"
        fonte_botao = pygame.font.Font(None, 50) #fonte do texto
        botao_texto = fonte_botao.render('JOGAR NOVAMENTE', True, (0, 255, 0))   # anti-alising true, renderiza a tela de derrota
        botao_rect = botao_texto.get_rect(center=(tela_width // 2, tela_height // 2 + 50))  # centralizar o texto de jogar novamente no meio da tela
        pygame.draw.rect(tela, (255, 255, 255), botao_rect.inflate(20, 20))  # Rect redor do texto
        tela.blit(botao_texto, botao_rect) #renderiza o botão pra reiniciar o jogo 

    elif derrota:
        # Desenhar a tela de derrota
        fonte = pygame.font.Font(None, 74) #fonte do texto
        texto = fonte.render('VOCÊ PERDEU!', True, (255, 0, 0))  # anti-alising true, renderiza o text de derrota
        texto_rect = texto.get_rect(center=(tela_width // 2, tela_height // 2 - 50)) #cria e centraliza o rect do texto
        tela.fill((255, 255, 255)) #preenche o resto da tela com a cor branca (pra esconder o contador kk)
        tela.blit(texto, texto_rect) #renderiza o texto e o rect

        # Desenhar o botão "Jogar Novamente"
        fonte_botao = pygame.font.Font(None, 50)
        botao_texto = fonte_botao.render('JOGAR NOVAMENTE', True, (255, 0, 0))   # anti-alising true, renderiza o texto de jogar novamente
        botao_rect = botao_texto.get_rect(center=(tela_width // 2, tela_height // 2 + 50))  # criar e centralizar o texto de jogar novamente no meio da tela
        pygame.draw.rect(tela, (255, 255, 255), botao_rect.inflate(20, 20))  # rect azul ao redor do texto
        tela.blit(botao_texto, botao_rect) #renderiza o texto e o rect

    else:
        # Atualizar nave do jogador
        pos_mouse = pygame.mouse.get_pos()[0] #retorna a posição atual do mouse (x, y), o [0] pega a coordenada x(horizontal)
        jogador.x += (pos_mouse - jogador.centerx) * suavizacao # calcula a diferença entre a posição horizontal do mouse e a posição horizontal central da nave do jogador. 
        #Isso dá a quantidade de deslocamento que a nave precisa se mover para se alinhar com o mouse

        # Desenhar nave do jogador
        tela.blit(imagem_nave_original, jogador)

        # Movimento da nave inimiga
        nave_inimiga.x += velocidade_nave_inimiga * direcao_nave_inimiga * controle_fps #controla a movimentação horizontal da nave (1para direita, -1 para esquerda), sem a variável de controle de fps o jogo buga
        if nave_inimiga.right >= tela_width or nave_inimiga.left <= 0: #verifica se a nave chegou no limite da tela, esquerda ou direita
            direcao_nave_inimiga *= -1 #caso tenha chegado, multiplica o valor da direção por -1, pra inverter a direção do movimento

        
     
        if direcao_nave_inimiga == -1: #se estiver indo para a esquerda, renderiza a imagem virada para a esquerda
            imagem_nave_atual = imagem_nave_inimiga_esquerda
        else: #se estiver indo para a direita, renderiza a imagem virada para a direta
            imagem_nave_atual = imagem_nave_inimiga_direita

        # Desenhar a nave inimiga na tela
        tela.blit(imagem_nave_atual, nave_inimiga) #desenha a imagem_nave_atual no rect da nave_inimiga

        # Resetar o estado de atingida
        atingida = False

        # Desenhar projéteis
        for projetil in projeteis: #percorre a lista projeteis, necessária para gerenciar o comportamento de cada laser
            projetil.y += projetil_velocidade * controle_fps # o laser no eixo y recebe a velocidade do projetil_velocidade
            tela.blit(imagem_laser, projetil) # desenha a imagem_laser em projetil

        # Verificar se o laser atingiu a nave inimiga
        for projetil in projeteis: #percorre a lista projeteis, necessária para gerenciar o comportamento de cada laser
            if nave_inimiga.colliderect(projetil): #verifica se o retângulo da hitbox da nave inimiga colide com o retângulo do projetil
            #O método colliderect() é fornecido pelo Rect do Pygame e retorna True se houver interseção entre dois retangulos
              
                projeteis.remove(projetil) #Apaga o laser após o impacto, pra impedir que acerte a rect da nave novamente
                if nave_inimiga.width > tamanho_minimo: #verifica se a nave inimiga ainda é maior que a variável tamanho_minimo
                    redimensionar_nave() #caso seja maior, chama a função pra diminuir o tamanho da nave
                else:
                    vitoria = True #se a nave inimiga for menor ou igual ao tamanho minimo, o jogo encerra com vitória

        #pygame.mouse.get_pressed()[0] verifica o click esquerdo do mouse, and limitar a taxa de disparo dos projéteis.
        if pygame.mouse.get_pressed()[0] and pygame.time.get_ticks() - ultimo_tiro >= tempo_entre_tiros: 
            
            #jogador.centerx - 20: Define a posição horizontal (X) do laser. Ele é centralizado em relação a nave do jogador (jogador.centerx),
            # com um deslocamento de 20 pixels para garantir que o laser se alinhe com a nave
            #jogador.top - 20: Define a posição vertical (Y) do laser acima da nave (jogador.top - 20)
            #40, 40: Define a largura e a altura do laser. Aqui, o laser tem um tamanho quadrado de 40 por40
            #projeteis.append(...): O novo laser é adicionado à lista projeteis, que mantém o controle de todos os projéteis ativos no jogo.
            projeteis.append(pygame.Rect(jogador.centerx - 20, jogador.top - 20, 40, 40)) #posição onde o laser vai aparecer (posição, direção,width, height)
            ultimo_tiro = pygame.time.get_ticks() # atualiza o valor do último tiro, pra garantir que apenas um projeto por segundo seja disparado

    # contador
    fonte_tempo = pygame.font.Font(None, 50) # none = fonte padrão
    minutos = tempo_restante // 60000 # tempo_restante // 60000 divide o tempo restante em milissegundos por 60k para pegar o número de minutos
    segundos = (tempo_restante % 60000) // 1000 #pega o resto da divisão por 60.000 ( o tempo abaixo de um minuto) e divide por 1000 para converter em segundos
    
    #condicionais para alterar o contador no fim de jogo
    if segundos >= 20:
        tempo_texto = fonte_tempo.render("Fim do mundo em {}:{:02d}".format(minutos, segundos), True, (255, 255, 255))  # anti-alising true
        tela.blit(tempo_texto, (50, 50))#tempo e posição (x,y)
    elif segundos < 20:
        tempo_texto = fonte_tempo.render("Fim do mundo em {}:{:02d}".format(minutos, segundos), True, (255, 0, 0))  # tornar o timer vermelho quando o tempo for menor que 20
        tela.blit(tempo_texto, (50, 50)) #tempo e posição (x,y)   
    elif segundos == 0 or vitoria:
        tempo_texto = ""
        tela.blit(tempo_texto)          

    # Atualizar a tela
    pygame.display.flip()

pygame.quit()

