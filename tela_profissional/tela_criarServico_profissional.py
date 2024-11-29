import flet as ft
from banco.conexao2 import supabase
from typing import Optional, Tuple

async def criar_servico_bd(id_profissional: int, nome: str, descricao: str, valor: float) -> bool:
    try:
        dados_servico = {
            "nome": nome,
            "descricao": descricao,
            "valor": valor,
            "id_profissional": id_profissional
        }
        
        resultado = supabase.table('servicos')\
            .insert(dados_servico)\
            .execute()
        
        return len(resultado.data) > 0
    except Exception as e:
        print(f"Erro ao criar serviço: {e}")
        return False

async def criarServico(page: ft.Page):
    if not hasattr(page, 'session_data'):
        page.session_data = {}
        page.go('/login')
        return
        
    page.title = 'STASH - Criar Serviço'
    page.bgcolor = '#FFFFFF'
    page.scroll = 'auto'

    page.fonts = {
        'Poppins Medium': 'Poppins-Medium.ttf',
        'Poppins Regular': 'Poppins-Regular.ttf',
        'Poppins Bold': 'fonts/Poppins-Bold.ttf',
        'Poppins Semi-Bold': 'fonts/Poppins-SemiBold.ttf'
    }

    id_profissional = page.session_data.get("user_id")
    if not id_profissional:
        page.go('/login')
        return

    try:
        resultado = supabase.table('profissionais')\
            .select('nome, sobrenome, avatar_url')\
            .eq('id_profissional', id_profissional)\
            .limit(1)\
            .execute()
        
        if resultado.data:
            profissional = resultado.data[0]
            nome_completo = f"{profissional['nome']} {profissional['sobrenome']}"
            avatar_url = profissional.get('avatar_url')
        else:
            nome_completo = "Profissional"
            avatar_url = None
    except Exception as e:
        print(f"Erro ao buscar dados do profissional: {e}")
        nome_completo = "Profissional"
        avatar_url = None

    info_profissional = ft.Container(
        ft.Column([
            ft.Container(
                ft.CircleAvatar(
                    foreground_image_url=avatar_url if avatar_url else None,
                    content=ft.Icon(ft.icons.PERSON) if not avatar_url else None,
                    radius=30
                ),
                alignment=ft.alignment.center,
                margin=ft.margin.only(top=15, bottom=5)
            ),
            ft.Text(
                value=nome_completo,
                size=16,
                text_align=ft.TextAlign.CENTER,
                color='black',
                font_family='Poppins Medium'
            )
        ], 
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
        ),
        alignment=ft.alignment.center
    )

    nome_input = ft.TextField(
        border_radius=8,
        border_color='black',
        focused_border_color='#2ECC71',
        color='black',
        cursor_color='#2ECC71',
        width=340,
        height=45,
        hint_text="Nome do serviço...",
        text_style=ft.TextStyle(size=14),
        bgcolor='white'
    )

    nome_layout = ft.Container(
        content=ft.Column([
            ft.Text(
                value='Nome',
                size=16,
                color='black',
                font_family='Poppins Semi-Bold'
            ),
            ft.Container(
                nome_input,
                padding=ft.padding.only(top=5)
            )
        ]),
        alignment=ft.alignment.center,
        padding=ft.padding.only(left=20, right=20, top=15),
    )

    descricao_input = ft.TextField(
        border_radius=8,
        border_color='black',
        focused_border_color='#2ECC71',
        color='black',
        cursor_color='#2ECC71',
        width=340,
        min_lines=3,
        max_lines=3,
        multiline=True,
        text_style=ft.TextStyle(size=14),
        hint_text="Descrição do serviço...",
        bgcolor='white'
    )

    desc_layout = ft.Container(
        content=ft.Column([
            ft.Text(
                value='Descrição',
                size=16,
                color='black',
                font_family='Poppins Semi-Bold'
            ),
            ft.Container(
                descricao_input,
                padding=ft.padding.only(top=5)
            )
        ]),
        alignment=ft.alignment.center,
        padding=ft.padding.only(left=20, right=20, top=15),
    )

    def formatar_valor_monetario(e):
        texto = e.control.value
        numeros = ''.join(char for char in texto if char.isdigit())
        if numeros:
            valor = float(numeros) / 100
            if valor > 999.99:
                valor = 00.00
            e.control.value = f"{valor:.2f}".replace('.', ',')
        else:
            e.control.value = ''
        e.control.update()

    valor_input = ft.TextField(
        border_radius=8,
        border_color='black',
        focused_border_color='#2ECC71',
        color='black',
        cursor_color='#2ECC71',
        width=192,
        height=45,
        text_style=ft.TextStyle(size=14),
        hint_text='00,00',
        hint_style=ft.TextStyle(size=14),
        bgcolor='white',
        text_align=ft.TextAlign.CENTER,
        on_change=formatar_valor_monetario
    )

    valor_layout = ft.Container(
        content=ft.Column([
            ft.Text(
                value='Valor',
                size=16,
                color='black',
                font_family='Poppins Semi-Bold',
                text_align=ft.TextAlign.CENTER
            ),
            ft.Container(
                ft.Column([
                    valor_input,
                    ft.Text(
                        value="Preço da hora",
                        size=12,
                        color='#2ECC71',
                        text_align=ft.TextAlign.CENTER
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=ft.padding.only(top=5)
            )
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
        ),
        alignment=ft.alignment.center,
        padding=ft.padding.only(left=20, right=20, top=15),
    )

    async def mostrar_mensagem(mensagem: str):
        snack = ft.SnackBar(content=ft.Text(mensagem))
        page.overlay.append(snack)
        snack.open = True
        page.update()

    async def salvar_servico(e):
        nome = nome_input.value
        descricao = descricao_input.value
        valor_texto = valor_input.value

        if not all([nome, descricao, valor_texto]):
            await mostrar_mensagem("Por favor, preencha todos os campos")
            return

        try:
            valor = float(valor_texto.replace(',', '.'))
            if valor <= 0:
                await mostrar_mensagem("O valor deve ser maior que zero")
                return
        except ValueError:
            await mostrar_mensagem("Por favor, insira um valor válido")
            return

        if len(nome) > 20:
            await mostrar_mensagem("O nome do serviço deve ter no máximo 20 caracteres")
            return

        if await criar_servico_bd(id_profissional, nome, descricao, valor):
            await mostrar_mensagem("Serviço criado com sucesso!")
            page.go('/listar-servico')
        else:
            await mostrar_mensagem("Erro ao criar serviço")

    btn = ft.Container(
        ft.ElevatedButton(
            content=ft.Text(
                value='Criar',
                size=16,
                color='#FFFFFF',
                font_family='Poppins Semi-Bold'
            ),
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=15),
                bgcolor='#2ECC71'
            ),
            width=192,
            height=42,
            on_click=salvar_servico
        ),
        alignment=ft.alignment.center,
        padding=ft.padding.only(top=20, left=20, right=20)
    )

    page.add(
        info_profissional,
        nome_layout,
        desc_layout,
        valor_layout,
        btn
    )