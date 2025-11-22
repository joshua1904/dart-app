import { Component, createRef } from "preact";
import register from "preact-custom-element";

interface Props {
    info: string;
}

interface State {
    showInfo: boolean;
}
export class InfoButton extends Component<Props, State> {
    static tagName = "info-button";
    private dialogRef = createRef<HTMLDialogElement>();
    constructor(props: Props) {
        super(props);
        this.state = {showInfo: false};
    }
    private openDialog = () => {
        const dialog = this.dialogRef.current;
        if (dialog && typeof dialog.showModal === "function") {
            dialog.showModal();
        } else {
            this.setState({showInfo: true});
        }
    }
    private closeDialog = () => {
        const dialog = this.dialogRef.current;
        if (dialog && dialog.open) {
            dialog.close();
        }
        if (this.state.showInfo) {
            this.setState({showInfo: false});
        }
    }
    render() {
        return (
        <>
         <button
            type="button"
            class="btn btn-outline-secondary btn-sm rounded-circle"
            title="Info"
            aria-label="Info"
            aria-haspopup="dialog"
            onClick={this.openDialog}>
            <i class="bi bi-info-circle"></i>
        </button>
        <dialog ref={this.dialogRef} aria-labelledby="info-title" onClose={this.closeDialog}>
            <h3 id="info-title">Info</h3>
            <p>{this.props.info}</p>
            <div style="text-align: right; margin-top: 1rem;">
                <button type="button" class="btn btn-secondary btn-sm" onClick={this.closeDialog} aria-label="Close">
                    Close
                </button>
            </div>
            <style>
                {`dialog { border: none; border-radius: 12px; padding: 1rem 1.25rem; max-width: 480px; width: calc(100% - 2rem); }
                  dialog::backdrop { background: rgba(0, 0, 0, 0.5); }`}
            </style>
        </dialog>
        </>
        )
    }
}
register(InfoButton);