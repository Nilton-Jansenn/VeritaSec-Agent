from __future__ import annotations

from fastapi.responses import Response


_JS = r'''
(() => {

"use strict";

/*
 * VERITASSEC_BROWSER_PROBE_JS_20261019
 */

function vsProbe(etapa) {

    try {

        fetch(
            "/api/interface/browser-probe?etapa="
            + encodeURIComponent(etapa),
            {
                method:
                    "GET",

                cache:
                    "no-store"
            }
        ).catch(
            () => {}
        );

    } catch (_) {
        /* diagnóstico não pode interromper a UI */
    }
}


vsProbe(
    "01_CARREGADO"
);


window.addEventListener(
    "error",
    (evento) => {

        vsProbe(
            "ERRO_RUNTIME:"
            + (
                evento?.message
                || "sem_mensagem"
            )
            + ":"
            + (
                evento?.lineno
                || 0
            )
        );
    }
);


if (
    window.__veritasSecSeletorPersistente
) {
    return;
}


window.__veritasSecSeletorPersistente =
    true;


let modo =
    null;

let atual =
    null;

let pai =
    null;

let instalando =
    false;


const el = (id) =>
    document.getElementById(id);


/* ============================================================
 * MODAL
 * ============================================================ */

function garantirModal() {

    if (
        el("vsPersistFsModal")
    ) {
        return;
    }


    const modal =
        document.createElement(
            "div"
        );


    modal.id =
        "vsPersistFsModal";


    modal.innerHTML = `
<div id="vsPersistFsJanela">

    <div id="vsPersistFsTopo">

        <h2 id="vsPersistFsTitulo">
            Selecionar
        </h2>

        <div id="vsPersistFsBarra">

            <button
                id="vsPersistFsSubir"
                type="button"
            >
                ↑ Subir
            </button>

            <input
                id="vsPersistFsCaminho"
                type="text"
                readonly
            >

            <button
                id="vsPersistFsFechar"
                type="button"
            >
                Fechar
            </button>

        </div>

    </div>


    <div id="vsPersistFsAjuda"></div>


    <div id="vsPersistFsLista"></div>


    <div id="vsPersistFsRodape">

        <button
            id="vsPersistFsEscolherPasta"
            type="button"
        >
            Selecionar esta pasta
        </button>

        <button
            id="vsPersistFsCancelar"
            type="button"
        >
            Cancelar
        </button>

    </div>

</div>
`;


    document.body.appendChild(
        modal
    );


    el(
        "vsPersistFsFechar"
    ).onclick =
        fechar;


    el(
        "vsPersistFsCancelar"
    ).onclick =
        fechar;


    el(
        "vsPersistFsSubir"
    ).onclick =
        async () => {

            if (pai) {

                await carregar(
                    pai
                );
            }
        };


    el(
        "vsPersistFsEscolherPasta"
    ).onclick =
        () => {

            if (
                modo !== "projeto"
                || !atual
            ) {

                return;
            }


            definir(
                "projeto",
                atual
            );


            fechar();
        };


    modal.onclick =
        (evento) => {

            if (
                evento.target === modal
            ) {

                fechar();
            }
        };
}


function fechar() {

    el(
        "vsPersistFsModal"
    )?.classList.remove(
        "aberto"
    );
}


/* ============================================================
 * BACKEND
 * ============================================================ */

async function consultar(
    caminho = null
) {

    const params =
        new URLSearchParams();


    params.set(
        "tipo",
        (
            modo === "sarif"
            ? "sarif"
            : "diretorio"
        )
    );


    if (caminho) {

        params.set(
            "path",
            caminho
        );
    }


    const resposta =
        await fetch(
            "/api/interface/fs?"
            + params.toString(),
            {
                cache:
                    "no-store"
            }
        );


    let dados = {};


    try {

        dados =
            await resposta.json();

    } catch (_) {

        dados = {};
    }


    if (!resposta.ok) {

        throw new Error(
            dados?.detail
            || (
                "HTTP "
                + resposta.status
            )
        );
    }


    return dados;
}


/* ============================================================
 * DEFINE SELECAO
 * ============================================================ */

function definir(
    tipo,
    caminho
) {

    const picker =
        el(
            tipo === "projeto"
            ? "projetoPicker"
            : "sarifPicker"
        );


    const select =
        el(
            tipo === "projeto"
            ? "projeto"
            : "sarif"
        );


    if (picker) {

        picker.value =
            caminho;
    }


    if (select) {

        select.innerHTML =
            "";


        const option =
            document.createElement(
                "option"
            );


        option.value =
            caminho;

        option.textContent =
            caminho;

        option.selected =
            true;


        select.appendChild(
            option
        );


        select.value =
            caminho;


        select.dispatchEvent(
            new Event(
                "change",
                {
                    bubbles:
                        true
                }
            )
        );
    }
}


/* ============================================================
 * LISTAGEM
 * ============================================================ */

async function carregar(
    caminho = null
) {

    const dados =
        await consultar(
            caminho
        );


    atual =
        dados.atual;

    pai =
        dados.pai;


    el(
        "vsPersistFsCaminho"
    ).value =
        atual || "";


    const lista =
        el(
            "vsPersistFsLista"
        );


    lista.innerHTML =
        "";


    if (
        modo === "projeto"
    ) {

        el(
            "vsPersistFsTitulo"
        ).textContent =
            "Selecionar diretório do projeto";


        el(
            "vsPersistFsAjuda"
        ).textContent =
            (
                "Navegue até a pasta desejada "
                + "e clique em “Selecionar esta pasta”."
            );


        el(
            "vsPersistFsEscolherPasta"
        ).style.display =
            "";

    } else {

        el(
            "vsPersistFsTitulo"
        ).textContent =
            "Selecionar arquivo SARIF";


        el(
            "vsPersistFsAjuda"
        ).textContent =
            (
                "Navegue pelas pastas e clique "
                + "diretamente no arquivo .sarif."
            );


        el(
            "vsPersistFsEscolherPasta"
        ).style.display =
            "none";
    }


    for (
        const item
        of dados.itens || []
    ) {

        const botao =
            document.createElement(
                "button"
            );


        botao.type =
            "button";

        botao.className =
            "vsPersistFsItem";


        botao.textContent =
            (
                item.tipo === "diretorio"
                ? "📁 "
                : "📄 "
            )
            + item.nome;


        botao.onclick =
            async () => {

                if (
                    item.tipo
                    === "diretorio"
                ) {

                    await carregar(
                        item.caminho
                    );

                    return;
                }


                if (
                    modo === "sarif"
                ) {

                    definir(
                        "sarif",
                        item.caminho
                    );


                    fechar();
                }
            };


        lista.appendChild(
            botao
        );
    }


    if (
        !dados.itens
        || dados.itens.length === 0
    ) {

        const vazio =
            document.createElement(
                "div"
            );


        vazio.className =
            "vsPersistFsVazio";


        vazio.textContent =
            (
                modo === "sarif"
                ? "Nenhuma pasta ou arquivo SARIF encontrado."
                : "Diretório vazio."
            );


        lista.appendChild(
            vazio
        );
    }
}


/* ============================================================
 * ABERTURA
 * ============================================================ */

async function abrir(
    tipo
) {

    garantirModal();


    modo =
        tipo;


    el(
        "vsPersistFsModal"
    ).classList.add(
        "aberto"
    );


    el(
        "vsPersistFsLista"
    ).textContent =
        "Carregando...";


    try {

        await carregar();

    } catch (erro) {

        el(
            "vsPersistFsLista"
        ).textContent =
            (
                "Erro ao carregar diretórios: "
                + erro.message
            );
    }
}


/* ============================================================
 * BOTAO PERSISTENTE
 * ============================================================ */

function colocarBotao(
    pickerId,
    botaoId,
    texto,
    tipo
) {

    const picker =
        el(
            pickerId
        );


    if (!picker) {

        return;
    }


    picker.readOnly =
        true;


    picker.style.cursor =
        "default";


    let botao =
        el(
            botaoId
        );


    if (!botao) {

        botao =
            document.createElement(
                "button"
            );


        botao.id =
            botaoId;

        botao.type =
            "button";

        botao.className =
            "vsPersistBotao";


        picker.insertAdjacentElement(
            "afterend",
            botao
        );
    }


    botao.textContent =
        texto;


    botao.style.setProperty(
        "display",
        "inline-flex",
        "important"
    );


    botao.style.setProperty(
        "visibility",
        "visible",
        "important"
    );


    botao.style.setProperty(
        "opacity",
        "1",
        "important"
    );


    botao.onclick =
        (evento) => {

            evento.preventDefault();

            evento.stopPropagation();

            evento.stopImmediatePropagation();


            abrir(
                tipo
            );
        };
}


/* ============================================================
 * INSTALACAO
 * ============================================================ */

function instalar() {

    vsProbe(
        "02_ENTROU_INSTALAR"
    );

    if (instalando) {

        return;
    }


    instalando =
        true;


    try {

        vsProbe(
            el("projetoPicker")
            ? "03_PICKER_PROJETO_SIM"
            : "03_PICKER_PROJETO_NAO"
        );

        colocarBotao(
            "projetoPicker",
            "vsPersistSelecionarDiretorio",
            "Selecionar Diretório",
            "projeto"
        );

        vsProbe(
            el("vsPersistSelecionarDiretorio")
            ? "04_BOTAO_PROJETO_SIM"
            : "04_BOTAO_PROJETO_NAO"
        );


        vsProbe(
            el("sarifPicker")
            ? "05_PICKER_SARIF_SIM"
            : "05_PICKER_SARIF_NAO"
        );

        colocarBotao(
            "sarifPicker",
            "vsPersistSelecionarSarif",
            "Selecionar SARIF",
            "sarif"
        );

        vsProbe(
            el("vsPersistSelecionarSarif")
            ? "06_BOTAO_SARIF_SIM"
            : "06_BOTAO_SARIF_NAO"
        );


    } finally {

        instalando =
            false;

        vsProbe(
            "07_SAIU_INSTALAR"
        );
    }
}


instalar();


if (
    document.readyState
    === "loading"
) {

    document.addEventListener(
        "DOMContentLoaded",
        instalar,
        {
            once:
                true
        }
    );
}


/*
 * Mantém os botões mesmo se scripts antigos
 * reconstruírem parte da interface.
 */
const observer =
    new MutationObserver(
        () => {

            if (
                !el(
                    "vsPersistSelecionarDiretorio"
                )
                || !el(
                    "vsPersistSelecionarSarif"
                )
            ) {

                instalar();
            }
        }
    );


observer.observe(
    document.documentElement,
    {
        childList:
            true,

        subtree:
            true
    }
);


/*
 * VERITASSEC_DIAGNOSTICO_LAYOUT_BROWSER_20261019
 */

function vsProbeLayoutElemento(
    nome,
    elemento
) {

    if (!elemento) {

        vsProbe(
            "LAYOUT_"
            + nome
            + "_AUSENTE"
        );

        return;
    }


    const css =
        getComputedStyle(
            elemento
        );


    const r =
        elemento.getBoundingClientRect();


    const pai =
        elemento.parentElement;


    const cssPai =
        pai
        ? getComputedStyle(
            pai
        )
        : null;


    const rp =
        pai
        ? pai.getBoundingClientRect()
        : null;


    const dados = [
        "LAYOUT",
        nome,

        "DISPLAY",
        css.display,

        "VIS",
        css.visibility,

        "OP",
        css.opacity,

        "POS",
        css.position,

        "W",
        Math.round(r.width),

        "H",
        Math.round(r.height),

        "X",
        Math.round(r.x),

        "Y",
        Math.round(r.y),

        "PAI",
        pai?.tagName
            || "NULL",

        "PAI_ID",
        pai?.id
            || "-",

        "PAI_CLASS",
        (
            pai?.className
            || "-"
        )
        .toString()
        .replaceAll(
            " ",
            "."
        ),

        "PAI_DISPLAY",
        cssPai?.display
            || "-",

        "PAI_OVERFLOW",
        cssPai?.overflow
            || "-",

        "PAI_W",
        rp
        ? Math.round(rp.width)
        : -1,

        "PAI_H",
        rp
        ? Math.round(rp.height)
        : -1,
    ];


    vsProbe(
        dados.join(
            "|"
        )
    );
}


function vsExecutarProbeLayout() {

    vsProbeLayoutElemento(
        "PROJETO_PICKER",
        el(
            "projetoPicker"
        )
    );


    vsProbeLayoutElemento(
        "BOTAO_PROJETO",
        el(
            "vsPersistSelecionarDiretorio"
        )
    );


    vsProbeLayoutElemento(
        "SARIF_PICKER",
        el(
            "sarifPicker"
        )
    );


    vsProbeLayoutElemento(
        "BOTAO_SARIF",
        el(
            "vsPersistSelecionarSarif"
        )
    );


    const bp =
        el(
            "vsPersistSelecionarDiretorio"
        );


    const bs =
        el(
            "vsPersistSelecionarSarif"
        );


    if (bp) {

        vsProbe(
            "BOTAO_PROJETO_IS_CONNECTED="
            + String(
                bp.isConnected
            )
        );
    }


    if (bs) {

        vsProbe(
            "BOTAO_SARIF_IS_CONNECTED="
            + String(
                bs.isConnected
            )
        );
    }
}


setTimeout(
    vsExecutarProbeLayout,
    500
);


setTimeout(
    vsExecutarProbeLayout,
    1500
);


setTimeout(
    vsExecutarProbeLayout,
    3000
);



window.veritasSecAbrirProjeto =
    () => abrir(
        "projeto"
    );


window.veritasSecAbrirSarif =
    () => abrir(
        "sarif"
    );


})();
'''


_CSS = r'''

/*
 * VERITASSEC_LAYOUT_SELETORES_20261019
 *
 * Reserva espaço visível para os botões de seleção.
 */

#projetoPicker,
#sarifPicker {

    display:
        inline-block !important;

    width:
        calc(100% - 185px) !important;

    max-width:
        calc(100% - 185px) !important;

    min-width:
        220px !important;

    box-sizing:
        border-box !important;

    vertical-align:
        middle !important;
}


#vsPersistSelecionarDiretorio,
#vsPersistSelecionarSarif {

    display:
        inline-flex !important;

    visibility:
        visible !important;

    opacity:
        1 !important;

    width:
        170px !important;

    min-width:
        170px !important;

    max-width:
        170px !important;

    height:
        32px !important;

    margin-left:
        8px !important;

    vertical-align:
        middle !important;

    position:
        static !important;
}


@media(max-width:900px) {

    #projetoPicker,
    #sarifPicker {

        width:
            calc(100% - 160px) !important;

        max-width:
            calc(100% - 160px) !important;

        min-width:
            180px !important;
    }


    #vsPersistSelecionarDiretorio,
    #vsPersistSelecionarSarif {

        width:
            145px !important;

        min-width:
            145px !important;

        max-width:
            145px !important;
    }
}



#projetoPicker,
#sarifPicker {

    cursor:
        default !important;

    background:
        #ffffff !important;
}


#vsPersistSelecionarDiretorio,
#vsPersistSelecionarSarif {

    display:
        inline-flex !important;

    visibility:
        visible !important;

    opacity:
        1 !important;

    align-items:
        center;

    justify-content:
        center;

    min-width:
        165px;

    height:
        32px;

    margin-left:
        8px;

    padding:
        0 14px;

    border:
        1px solid
        #8c99a6;

    border-radius:
        4px;

    background:
        #eef1f4;

    color:
        #17212b;

    cursor:
        pointer;

    white-space:
        nowrap;
}


#vsPersistSelecionarDiretorio:hover,
#vsPersistSelecionarSarif:hover {

    border-color:
        #174ea6;

    background:
        #dfe6ed;
}


/*
 * Desativa os seletores experimentais antigos.
 */
#vsFsExtModal,
#vsFsDiretoModal,
#vsFsDefModal {

    display:
        none !important;
}


#vsPersistFsModal {

    position:
        fixed;

    inset:
        0;

    display:
        none;

    align-items:
        center;

    justify-content:
        center;

    z-index:
        2147483647;

    background:
        rgba(0,0,0,.64);
}


#vsPersistFsModal.aberto {

    display:
        flex !important;
}


#vsPersistFsJanela {

    width:
        min(
            1000px,
            94vw
        );

    height:
        min(
            720px,
            86vh
        );

    display:
        flex;

    flex-direction:
        column;

    overflow:
        hidden;

    background:
        #fff;

    border-radius:
        10px;

    box-shadow:
        0 24px 75px
        rgba(0,0,0,.40);
}


#vsPersistFsTopo {

    padding:
        14px;

    border-bottom:
        1px solid
        #d7dde5;
}


#vsPersistFsBarra {

    display:
        grid;

    grid-template-columns:
        auto
        1fr
        auto;

    gap:
        8px;
}


#vsPersistFsCaminho {

    width:
        100%;

    font-family:
        monospace;
}


#vsPersistFsAjuda {

    padding:
        10px 14px;

    background:
        #f8fafc;

    border-bottom:
        1px solid
        #d7dde5;
}


#vsPersistFsLista {

    flex:
        1;

    overflow:
        auto;

    padding:
        8px;
}


.vsPersistFsItem {

    display:
        block;

    width:
        100%;

    margin:
        2px 0;

    padding:
        10px 12px;

    border:
        0;

    border-radius:
        5px;

    background:
        #f7f9fc;

    text-align:
        left;

    cursor:
        pointer;
}


.vsPersistFsItem:hover {

    background:
        #e5edf8;
}


.vsPersistFsVazio {

    padding:
        20px;
}


#vsPersistFsRodape {

    display:
        flex;

    justify-content:
        flex-end;

    gap:
        8px;

    padding:
        12px;

    border-top:
        1px solid
        #d7dde5;
}

'''


def interface_fs_javascript():

    return Response(
        content=_JS,
        media_type="application/javascript",
        headers={
            "Cache-Control":
                "no-store, no-cache, must-revalidate, max-age=0",

            "Pragma":
                "no-cache",
        },
    )


def interface_fs_css():

    return Response(
        content=_CSS,
        media_type="text/css",
        headers={
            "Cache-Control":
                "no-store, no-cache, must-revalidate, max-age=0",

            "Pragma":
                "no-cache",
        },
    )
