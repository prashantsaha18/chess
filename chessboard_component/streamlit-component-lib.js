/**
 * Standalone, lightweight streamlit-component-lib.js implementation.
 * Exposes Streamlit communication layer for iframe components.
 */

var ComponentMessageType;
(function (ComponentMessageType) {
    ComponentMessageType["COMPONENT_READY"] = "streamlit:componentReady";
    ComponentMessageType["SET_COMPONENT_VALUE"] = "streamlit:setComponentValue";
    ComponentMessageType["SET_FRAME_HEIGHT"] = "streamlit:setFrameHeight";
})(ComponentMessageType || (ComponentMessageType = {}));

var Streamlit = {
    API_VERSION: 1,
    RENDER_EVENT: "streamlit:render",
    events: new EventTarget(),
    registeredMessageListener: false,
    lastFrameHeight: undefined,

    setComponentReady: function () {
        if (!Streamlit.registeredMessageListener) {
            window.addEventListener("message", Streamlit.onMessageEvent);
            Streamlit.registeredMessageListener = true;
        }
        Streamlit.sendBackMsg(ComponentMessageType.COMPONENT_READY, {
            apiVersion: Streamlit.API_VERSION
        });
    },

    setFrameHeight: function (height) {
        if (height === undefined) {
            height = document.body.scrollHeight;
        }
        if (height === Streamlit.lastFrameHeight) {
            return;
        }
        Streamlit.lastFrameHeight = height;
        Streamlit.sendBackMsg(ComponentMessageType.SET_FRAME_HEIGHT, { height: height });
    },

    setComponentValue: function (value) {
        Streamlit.sendBackMsg(ComponentMessageType.SET_COMPONENT_VALUE, {
            value: value,
            dataType: "json"
        });
    },

    onMessageEvent: function (event) {
        var type = event.data["type"];
        switch (type) {
            case Streamlit.RENDER_EVENT:
                Streamlit.onRenderMessage(event.data);
                break;
        }
    },

    onRenderMessage: function (data) {
        var args = data["args"];
        if (args == null) {
            args = {};
        }
        var disabled = Boolean(data["disabled"]);
        var theme = data["theme"];
        if (theme) {
            Streamlit.injectTheme(theme);
        }
        var eventData = { disabled: disabled, args: args, theme: theme };
        var event = new CustomEvent(Streamlit.RENDER_EVENT, {
            detail: eventData
        });
        Streamlit.events.dispatchEvent(event);
    },

    injectTheme: function (theme) {
        var style = document.createElement("style");
        document.head.appendChild(style);
        style.innerHTML = `
            :root {
                --primary-color: ${theme.primaryColor};
                --background-color: ${theme.backgroundColor};
                --secondary-background-color: ${theme.secondaryBackgroundColor};
                --text-color: ${theme.textColor};
                --font: ${theme.font};
            }
            body {
                background-color: var(--background-color);
                color: var(--text-color);
            }
        `;
    },

    sendBackMsg: function (type, data) {
        window.parent.postMessage(Object.assign({ isStreamlitMessage: true, type: type }, data), "*");
    }
};

window.Streamlit = Streamlit;
