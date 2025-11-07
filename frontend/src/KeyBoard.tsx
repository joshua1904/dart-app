import {Component} from "preact";
import register from "preact-custom-element";
import { ThreeThrowKeyBoard } from "./ThreeThrowKeyBoard";
import { SimpleKeyBoard } from "./SimpleKeyBoard";

enum KeyboardType {
    simple = 0,
    threeThrow = 1,
}

interface Props {
    keyboard: KeyboardType
}

interface State {
    keyboard: KeyboardType
}

export class KeyBoard extends Component<Props, State> {
    static tagName = "simple-keyboard";
     constructor(props: Props) {
         super(props);
         this.state = {keyboard: props.keyboard ?? 0};
     }
     toggleKeyBoard= () => {
         if(this.state.keyboard == KeyboardType.simple){
             this.setState({keyboard: KeyboardType.threeThrow})
         }
         else{
             this.setState({keyboard: KeyboardType.simple})
         }
}
     render() {
        return <>

            <input type="hidden" name="keyboard" value={this.state.keyboard}/>
            {this.state.keyboard == KeyboardType.simple ? <SimpleKeyBoard/> : <ThreeThrowKeyBoard/>}
            <div className="d-flex justify-content-end mb-2">
                <button
                    type="button"
                    className="btn btn-outline-secondary btn-sm rounded-circle"
                    title="Switch keyboard"
                    aria-label="Switch keyboard"
                    onClick={this.toggleKeyBoard}
                    style="width: 2rem; height: 2rem; display: flex; align-items: center; justify-content: center;"
                >
                    <i className="bi bi-arrow-left-right"></i>
                </button>
            </div>
        </>
     }
}


register(KeyBoard, 'key-board', [], {shadow: false})