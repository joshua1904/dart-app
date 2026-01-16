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
    score_left: string
}

interface State {
    keyboard: KeyboardType
    points: number
    checkoutHint: string
    throws_left: number
}

export class KeyBoard extends Component<Props, State> {
    static tagName = "simple-keyboard";
     constructor(props: Props) {
         super(props);
         this.state = {keyboard: props.keyboard ?? 0, points: 0, checkoutHint: "", throws_left: 0};
         this.checkoutHint(0, 3);
     }
     checkoutHint = async (points: number, throwsLeft: number) => {
         const leftScore = parseInt(this.props.score_left) - points;
         const response = await fetch(`/checkout-hint/${leftScore}/${throwsLeft}`);
         const data = await response.json();
         this.setState({checkoutHint: data.checkout_suggestion});
     }



     toggleKeyBoard= () => {
         if(this.state.keyboard == KeyboardType.simple){
             this.setState({keyboard: KeyboardType.threeThrow})
         }
         else{
             this.setState({keyboard: KeyboardType.simple})
         }
}
    setPoints = (points: number, throwsLeft?:number) => {

        this.setState({points: points});
        if (throwsLeft){
            void this.checkoutHint(points, throwsLeft)
        }
    }
     render() {
        return <>
            {this.state.checkoutHint && (
                <div className="alert alert-info mb-3 py-1 px-2 text-center">
                    <small>{this.state.checkoutHint}</small>
                </div>
            )}
            <input type="hidden" name="keyboard" value={this.state.keyboard}/>
            {this.state.keyboard == KeyboardType.simple ? <SimpleKeyBoard points={this.state.points} setPoints={this.setPoints}/> : <ThreeThrowKeyBoard setPoints={this.setPoints}/>}
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