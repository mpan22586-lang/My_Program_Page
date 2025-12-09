import pygame
import random

# Pygameの初期化
pygame.init()

## 1. 定数と初期設定

# 画面設定
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 400
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("ジャンプランナー (Pygame)")

# 色の定義
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 100, 0)

# ゲームの速度設定
clock = pygame.time.Clock()
FPS = 60 # 1秒間に60回ループ

# フォント設定
font_large = pygame.font.Font(None, 74)
font_medium = pygame.font.Font(None, 36)

# 地面の位置
GROUND_Y = SCREEN_HEIGHT - 50

# スコア変数
score = 0
# スピード関連変数 (ここが重要)
BASE_SPEED = 7      # ゲーム開始時の基本速度
SPEED_INCREMENT = 0.005 # 1フレームあたりの速度増加量 (60FPSで1秒間に約0.3増加)

# -----------------------------------------------------
## 2. Sprite クラス定義

### プレイヤー (ランナー) クラス
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # 画像の代わりに四角形で表現
        self.image = pygame.Surface([50, 50])
        self.image.fill(GREEN)  # プレイヤーは緑色
        self.rect = self.image.get_rect()
        self.rect.x = 50
        self.rect.y = GROUND_Y
        self.vy = 0       # 垂直速度 (Vertical Velocity)
        self.on_ground = True
        self.gravity = 1  # 重力加速度

    def update(self):
        # 重力による落下
        self.vy += self.gravity
        self.rect.y += self.vy

        # 地面との衝突判定とリセット
        if self.rect.y >= GROUND_Y:
            self.rect.y = GROUND_Y
            self.vy = 0
            self.on_ground = True

    def jump(self):
        if self.on_ground:
            self.on_ground = False
            self.vy = -20 # ジャンプの初期速度
            
### 障害物 クラス
class Obstacle(pygame.sprite.Sprite):
    def __init__(self, speed):
        super().__init__()
        # 障害物のサイズをランダムに設定 (難易度調整)
        height = random.choice([40, 60, 80])
        width = random.randint(20, 50)
        self.image = pygame.Surface([width, height])
        self.image.fill(RED) # 障害物は赤色
        self.rect = self.image.get_rect()
        
        # 地面に合わせてY座標を設定
        # +50はプレイヤーとの描画を合わせるための微調整
        self.rect.x = SCREEN_WIDTH # 画面右端から出現
        self.rect.y = GROUND_Y - height + 50 
        self.speed = speed

    def update(self):
        # 左に流れる
        self.rect.x -= self.speed
        
# スコア表示関数
def draw_score(surface, score):
    score_text = font_medium.render(f"SCORE: {score}", True, BLACK)
    surface.blit(score_text, (SCREEN_WIDTH - 150, 10))
    
# ゲームオーバー表示関数
def draw_game_over(surface):
    game_over_text = font_large.render("GAME OVER", True, RED)
    text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
    surface.blit(game_over_text, text_rect)
    
    restart_text = font_medium.render("Click or Press SPACE to Restart", True, BLACK)
    restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 50))
    surface.blit(restart_text, restart_rect)

# -----------------------------------------------------
## 3. ゲームのメインループ

def main_game():
    global score
    
    # Spriteグループの作成
    all_sprites = pygame.sprite.Group()
    obstacles = pygame.sprite.Group()

    player = Player()
    all_sprites.add(player)

    game_over = False
    
    # 🏃‍♂️💨 速度が時間で上がるようにするための変数
    current_obstacle_speed = BASE_SPEED 
    
    spawn_counter = 0
    score = 0 # リスタート時にスコアをリセット

    running = True
    while running:
        # 速度を制御 (FPS=60)
        clock.tick(FPS)
        
        # イベント処理 (入力)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            # 画面タップ（マウスの左クリック）またはスペースキーでジャンプ
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if game_over:
                    # ゲームオーバー時にクリックで再起動
                    main_game() 
                    return
                else:
                    player.jump()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                 if game_over:
                    main_game()
                    return
                 else:
                    player.jump()

        if not game_over:
            # 1. 状態の更新
            all_sprites.update()
            
            # 難易度調整: スピードをだんだん上げる
            current_obstacle_speed += SPEED_INCREMENT 
            
            # スコアの更新 (時間経過で増加)
            score += 1
            
            # 障害物の生成
            spawn_counter += 1
            # 障害物の出現間隔をランダムにする (40〜100フレーム)
            if spawn_counter > random.randint(40, 100): 
                # 🚀 現在のスピードを Obstacle クラスに渡す
                new_obstacle = Obstacle(current_obstacle_speed) 
                all_sprites.add(new_obstacle)
                obstacles.add(new_obstacle)
                spawn_counter = 0

            # 画面外に出た障害物を消去
            for obs in obstacles:
                if obs.rect.x < -obs.rect.width:
                    obs.kill() # グループから削除する
                    
            # 衝突判定
            if pygame.sprite.spritecollideany(player, obstacles):
                game_over = True
                
            # 2. 描画
            screen.fill(WHITE) # 画面を白で塗りつぶす
            
            # 地面を描画
            pygame.draw.line(screen, BLACK, (0, GROUND_Y + 50), (SCREEN_WIDTH, GROUND_Y + 50), 5)
            
            all_sprites.draw(screen) # 全てのSpriteを描画
            draw_score(screen, score // 10) # スコアを10で割って見やすくする
            
        else:
            # ゲームオーバー時の描画
            screen.fill(WHITE)
            all_sprites.draw(screen) # 最後に衝突した状態を描画
            draw_game_over(screen)
            draw_score(screen, score // 10)

        # 描画内容を実際に画面に反映
        pygame.display.flip()

    pygame.quit()

# ゲーム開始
if __name__ == '__main__':
    main_game()