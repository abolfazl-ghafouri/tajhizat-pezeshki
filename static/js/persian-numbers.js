(() => {
    'use strict';

    const englishDigits = '0123456789';
    const arabicDigits = '٠١٢٣٤٥٦٧٨٩';
    const persianDigits = '۰۱۲۳۴۵۶۷۸۹';

    const digitMap = new Map();

    englishDigits.split('').forEach((digit, index) => {
        digitMap.set(digit, persianDigits[index]);
    });

    arabicDigits.split('').forEach((digit, index) => {
        digitMap.set(digit, persianDigits[index]);
    });

    const skipTags = new Set([
        'SCRIPT',
        'STYLE',
        'NOSCRIPT',
        'TEXTAREA',
        'INPUT',
        'SELECT',
        'OPTION',
    ]);

    const skipSelector = [
        '[data-no-persian]',
        '[contenteditable="true"]',
        '.no-persian',
    ].join(',');

    function toPersianDigits(text) {
        let result = '';

        for (const char of text) {
            result += digitMap.get(char) ?? char;
        }

        return result;
    }

    function shouldSkipElement(element) {
        return (
            skipTags.has(element.tagName)
            || element.matches(skipSelector)
            || element.closest(skipSelector)
        );
    }

    function convertTextNode(node) {
        const parent = node.parentElement;

        if (!parent || shouldSkipElement(parent)) {
            return;
        }

        const converted = toPersianDigits(node.nodeValue);

        if (converted !== node.nodeValue) {
            node.nodeValue = converted;
        }
    }

    function convertElement(root = document.body) {
        if (!root) {
            return;
        }

        if (
            root.nodeType === Node.ELEMENT_NODE
            && shouldSkipElement(root)
        ) {
            return;
        }

        const walker = document.createTreeWalker(
            root,
            NodeFilter.SHOW_TEXT,
            {
                acceptNode(node) {
                    return NodeFilter.FILTER_ACCEPT;
                },
            },
        );

        const nodes = [];
        let node;

        while ((node = walker.nextNode())) {
            nodes.push(node);
        }

        nodes.forEach(convertTextNode);
    }

    document.addEventListener('DOMContentLoaded', () => {
        convertElement();

        const observer = new MutationObserver((mutations) => {
            for (const mutation of mutations) {
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType !== Node.ELEMENT_NODE) {
                        if (node.nodeType === Node.TEXT_NODE) {
                            convertTextNode(node);
                        }
                        return;
                    }

                    convertElement(node);
                });

                if (mutation.type === 'characterData') {
                    convertTextNode(mutation.target);
                }
            }
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true,
            characterData: true,
        });
    });
})();
