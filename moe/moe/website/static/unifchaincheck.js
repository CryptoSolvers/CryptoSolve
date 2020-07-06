var unifSelect;
var chainSelect;
var allChainingAlgos;

function emptySelect(elements) {
    let length = elements.options.length;
    for (let i = length - 1; i >= 0; i--) {
        elements.options[i] = null;
    }
}

function unifchaincheck() {
    unifChosen = unifSelect.options[unifSelect.selectedIndex].value;
    if (unifChosen != 'p_unif' && unifChosen != 'xor_rooted_security') {
        // Add all the chanining options
        emptySelect(chainSelect);
        for (let i = 0; i < allChainingAlgos.length; i++) {
            chainSelect.options.add(allChainingAlgos[i].cloneNode(true))
        }
    } else {
        let supportedAlgos = [];
        if (unifChosen == 'p_unif') {
            supportedAlgos.push(...['cipher_block_chaining', 'propogating_cbc', 'hash_cbc']);
        } else { // xor_rooted_security
            supportedAlgos.push(...['cipher_feedback', 'output_feedback']);
        }
        emptySelect(chainSelect);
        for (let i = 0; i < allChainingAlgos.length; i++) {
            if (supportedAlgos.includes(allChainingAlgos[i].value)) {
                chainSelect.options.add(allChainingAlgos[i].cloneNode(true))
            }
        }
    }
}

function initialToolPageLoad() {
    unifSelect = document.querySelector('#unif');
    chainSelect = document.querySelector('#chaining');
    allChainingAlgos = chainSelect.cloneNode(true).options;
    unifSelect.addEventListener('change', unifchaincheck);
}

window.addEventListener('DOMContentLoaded', initialToolPageLoad);