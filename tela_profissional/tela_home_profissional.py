import flet as ft
from datetime import datetime
from banco.conexao2 import supabase
from typing import Optional, Tuple

def obter_hora():
    hora_atual = datetime.now().hour
    
    if 5 <= hora_atual < 12:
        return "Bom dia,"
    elif 12 <= hora_atual < 18:
        return "Boa tarde,"
    else:
        return "Boa noite,"

def cards_pronto(icon, text, on_click=None, disabled=False):
    return ft.Container(
        content=ft.Container(
            content=ft.Column(
                controls=[
                    ft.Container(
                        content=ft.Icon(
                            name=icon,
                            size=24,
                            color='white' if not disabled else 'grey'
                        ),
                        alignment=ft.alignment.center,
                    ),
                    ft.Container(
                        content=ft.Text(
                            value=text,
                            size=14,
                            color='white' if not disabled else 'grey',
                            font_family='Poppins Bold',
                            text_align=ft.TextAlign.CENTER,
                        ),
                        alignment=ft.alignment.center,
                        width=150,
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,  
                spacing=8
            ),
        ),
        width=150,
        height=100,
        border_radius=ft.border_radius.all(32),
        bgcolor='#2ECC71' if not disabled else '#E0E0E0',
        padding=15,
        alignment=ft.alignment.center,
        on_click=on_click if not disabled else None
    )

async def atualizar_status_profissional(id_profissional: int, novo_status: str) -> bool:
    try:
        resultado = supabase.table('profissionais')\
            .update({'status': novo_status})\
            .eq('id_profissional', id_profissional)\
            .execute()
        
        return len(resultado.data) > 0
    except Exception as e:
        print(f"Erro ao atualizar status: {e}")
        return False

async def home_profissional(page: ft.Page):
    if not hasattr(page, 'session_data'):
        page.session_data = {}
        page.go('/login')
        return

    page.bgcolor = "#FFFFFF"
    page.title = 'STASH - Home Profissional'
    page.scroll = ft.ScrollMode.AUTO
    
    id_profissional = page.session_data.get("user_id")
    if not id_profissional:
        page.go('/login')
        return

    try:
        resultado = supabase.table('profissionais')\
            .select('nome, sobrenome, status, profissao, avatar_url')\
            .eq('id_profissional', id_profissional)\
            .limit(1)\
            .execute()
        
        if resultado.data:
            profissional = resultado.data[0]
            nome_completo = f"{profissional['nome']} {profissional['sobrenome']}"
            status_atual = profissional['status']
            profissao = profissional['profissao']
            avatar_url = profissional.get('avatar_url')
        else:
            nome_completo = "Profissional"
            status_atual = "Indisponível"
            profissao = ""
            avatar_url = None
    except Exception as e:
        print(f"Erro ao buscar dados do profissional: {e}")
        nome_completo = "Profissional"
        status_atual = "Indisponível"
        profissao = ""
        avatar_url = None

    async def mudar_status(e):
        novo_status = "Disponível" if e.control.value == "green" else "Indisponível"
        if await atualizar_status_profissional(id_profissional, novo_status):
            mensagem = f"Status atualizado para {novo_status}"
        else:
            mensagem = "Erro ao atualizar status"
        
        snack = ft.SnackBar(content=ft.Text(mensagem))
        page.overlay.append(snack)
        snack.open = True
        page.update()

    titulo = ft.Container(
        content=ft.Row(
            controls=[
                ft.Container(
                    content=ft.Image(src='stash-logo-light.png'),
                    alignment=ft.alignment.center_left
                ),
                ft.Row(
                    controls=[
                        ft.Container(
                            content=ft.CircleAvatar(
                                foreground_image_url=avatar_url if avatar_url else None,
                                content=ft.Icon(ft.icons.PERSON) if not avatar_url else None,
                                radius=20
                            ),
                            on_click=lambda _: page.go('/configuracao-profissional')
                        )
                    ],
                    alignment=ft.MainAxisAlignment.END
                )
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        ),
        padding=ft.padding.only(top=25, left=0, right=15)
    )

    nome_profissional = ft.Row(
        controls=[
            ft.Container(
                ft.Row(
                    controls=[
                        ft.Text(value=f'{obter_hora()}', color='black', size=18, font_family='Poppins Bold'),
                        ft.Text(value=f'{nome_completo}', color='#2ECC71', size=18, font_family='Poppins Bold'),
                        ft.Text(value=f'!', color='black', size=18, font_family='Poppins Bold'),
                    ] 
                ),
                padding=ft.padding.only(left=20)
            )
        ]
    )

    radio_group = ft.RadioGroup(
        content=ft.Row([
            ft.Radio(
                value="green",
                label="Disponível",
                fill_color='#FFFFFF',
                label_style=ft.TextStyle(color='white')
            ),
            ft.Radio(
                value="red",
                label="Indisponível",
                fill_color='#FFFFFF',
                label_style=ft.TextStyle(color='white')
            )
        ], alignment=ft.MainAxisAlignment.CENTER),
        value="green" if status_atual == "Disponível" else "red",
        on_change=mudar_status
    )

    status_profissional = ft.Container(
        content=ft.Column([
            ft.Text(
                value='Status',
                size=14,
                color='white',
                font_family='Poppins Bold'
            ),
            radio_group
        ], alignment=ft.MainAxisAlignment.CENTER),
        bgcolor='#2ECC71',
        height=109,
        border_radius=ft.border_radius.all(30),
        margin=ft.margin.only(top=10, left=20, right=20),
        padding=20
    )

    profissional_titulo = ft.Container(
        ft.Row(controls=[ft.Text(value='Profissional', size=18, color='black', font_family='Poppins Bold')]),
        padding=ft.padding.only(left=20, top=10)
    )

    def criar(e): page.go('/criar-profissional')
    def solicitados(e): page.go('/servicos-solicitados')
    def listar(e): page.go('/listar-servico')
    def registros(e): page.go('/registros-servicos')

    cards = ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        cards_pronto(ft.icons.LIST_ALT, "Listar", listar),
                        cards_pronto(ft.icons.ASSIGNMENT, "Solicitados", solicitados),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=20
                ),
                ft.Row(
                    controls=[
                        cards_pronto(ft.icons.ADD, "Criar", criar),
                        cards_pronto(ft.icons.LIST_ALT_SHARP, "Registros", registros),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=20
                ),
            ],
            spacing=20,
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        margin=ft.margin.only(top=10),
        alignment=ft.alignment.center
    )

    page.add(
        titulo,
        nome_profissional,
        status_profissional,
        profissional_titulo,
        cards
    )