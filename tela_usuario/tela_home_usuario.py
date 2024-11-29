import flet as ft
from datetime import *
from banco.conexao2 import supabase

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
                        content=ft.Image(
                            src=icon,
                            border_radius=100,
                            width=55,
                            height=55
                        ),
                        alignment=ft.alignment.center,
                    ),
                    ft.Container(
                        content=ft.Text(
                            value=text,
                            size=14,
                            color='white' if not disabled else 'white',
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
        border_radius=ft.border_radius.all(20),
        bgcolor='#2ECC71' if not disabled else '',
        padding=15,
        alignment=ft.alignment.center,
        on_click=on_click if not disabled else None
    )

async def home_usuario(page: ft.Page):
    if not hasattr(page, 'session_data'):
        page.session_data = {}
        page.go('/login')
        return
    
    id_usuario = page.session_data.get("user_id")
    if not id_usuario:
        page.go('/login')
        return
    
    page.bgcolor = "#FFFFFF"

    try:
        resultado = supabase.table('pessoas')\
            .select('nome, sobrenome, avatar_url')\
            .eq('id_pessoa', id_usuario)\
            .limit(1)\
            .execute()
        
        if resultado.data:
            usuario = resultado.data[0]
            nome_completo = f"{usuario['nome']} {usuario['sobrenome']}"
            avatar_url = usuario.get('avatar_url')
        else:
            nome_completo = "Usuário"
            avatar_url = None
    except Exception as e:
        print(f"Erro ao buscar dados do usuário: {e}")
        nome_completo = "Usuário"
        avatar_url = None

    def listar(e, tipo_profissao: str):
        page.session_data["profissao_selecionada"] = tipo_profissao
        page.go('/listar-profissional')

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
                            on_click=lambda _: page.go('/configuracao-usuario')
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.END
                )
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        ),
        padding=ft.padding.only(top=25,left=0,right=15)
    )

    nome_usuario = ft.Row(
        controls=[
            ft.Container(
                ft.Row(
                    controls=[
                        ft.Text(value=f'{obter_hora()}', color='black', size=18, font_family='Poppins Bold'),
                        ft.Text(value=nome_completo, color='#00B74E', size=18, font_family='Poppins Bold'),
                        ft.Text(value=f'!', color='black', size=18, font_family='Poppins Bold')
                    ] 
                ),
                padding=ft.padding.only(left=20)
            )
        ]
    )

    pesquisar = ft.Container(
        content=ft.TextField(
            hint_text="Pesquisar...",
            width=500,
            height=45,
            suffix_icon=ft.icons.SEARCH,
            text_size=14,
            color='black',
            border_color='black',
            bgcolor='white',
            content_padding=ft.padding.only(left=10, top=0, bottom=0),
            cursor_color='#2ECC71',
            hint_style=ft.TextStyle(size=12, color='black', font_family='Poppins Regular'),
            focused_border_color='#2ECC71',
            border_radius=11
        ),
        alignment=ft.alignment.center,
        padding=ft.padding.only(left=15, right=15, top=10)
    )

    servicos = ft.Container(
        ft.Row(controls=[ft.Text(value='Serviços', size=18, color='black', font_family='Poppins Bold')]),
        padding=ft.padding.only(left=20, top=10)
    )

    cards = ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        cards_pronto('usuario/eletricista.png', "Eletricistas", lambda e: page.go('/listar-eletricistas')),
                        cards_pronto('usuario/pintor.png', "Pintores", lambda e: page.go('/listar-pintores')),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=20
                ),
                ft.Row(
                    controls=[
                        cards_pronto('usuario/jardineiro.png', "Jardineiros", lambda e: page.go('/listar-jardineiros')),
                        cards_pronto(ft.icons.LOCK, "", disabled=True),
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

    try:
        mais_pedidos_data = supabase.table('pessoa_servico')\
            .select('id_servico')\
            .execute()

        if mais_pedidos_data.data:
            contagem_servicos = {}
            for registro in mais_pedidos_data.data:
                id_servico = registro['id_servico']
                if id_servico in contagem_servicos:
                    contagem_servicos[id_servico] += 1
                else:
                    contagem_servicos[id_servico] = 1

            if contagem_servicos:
                id_servico_mais_pedido = max(contagem_servicos.items(), key=lambda x: x[1])[0]

                servico_popular = supabase.table('servicos')\
                    .select('*, profissionais(*)')\
                    .eq('id_servico', id_servico_mais_pedido)\
                    .execute()

                if servico_popular.data:
                    servico = servico_popular.data[0]
                    nome_servico = servico['nome']
                    valor_servico = servico['valor']
                    nome_prof = servico['profissionais']['nome']
                else:
                    nome_servico = "Serviço"
                    valor_servico = 0
                    nome_prof = "Profissional"
            else:
                nome_servico = "Serviço"
                valor_servico = 0
                nome_prof = "Profissional"
        else:
            nome_servico = "Serviço"
            valor_servico = 0
            nome_prof = "Profissional"

    except Exception as e:
        print(f"Erro ao buscar serviços populares: {e}")
        nome_servico = "Serviço"
        valor_servico = 0
        nome_prof = "Profissional"

    mais_pedidos = ft.Container(
        ft.Row(controls=[ft.Text(value='Mais pedidos', size=18, color='black', font_family='Poppins Bold')]),
        padding=ft.padding.only(left=20, top=10)
    )

    card_mais = ft.Container(
        content=ft.Row(
            controls=[
                ft.Container(
                    content=ft.Image(
                        src='usuario/4.png',
                        width=100,
                        border_radius=14
                    )
                ),
                ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Text(value=nome_prof, color='black', font_family='Poppins Bold', size=14)
                            ]
                        ),
                        ft.Row(
                            controls=[
                                ft.Text(value=nome_servico, color='black', font_family='Poppins Regular', size=14)
                            ]
                        ),
                        ft.Row(
                            controls=[
                                ft.Text(value=f'R$ {valor_servico:.2f}', color='#2ECC71', font_family='Poppins Bold', size=14)
                            ]
                        ),
                    ],
                    spacing=7
                )
            ]
        ),
        bgcolor='#D9D9D9',
        height=125,
        margin=ft.margin.only(left=15, right=15),
        alignment=ft.alignment.center,
        padding=ft.padding.only(left=20, top=10, bottom=10),
        border_radius=21
    )

    page.add(
        titulo,
        nome_usuario,
        pesquisar,
        servicos,
        cards,
        mais_pedidos,
        card_mais
    )