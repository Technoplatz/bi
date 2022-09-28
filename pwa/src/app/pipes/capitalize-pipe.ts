import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
    name: 'capitalize'
})

export class CapitalizePipe implements PipeTransform {
    transform(value: string, ...args: unknown[]): string {
        const unicodeWordMatch = /\w\S*/g;
        return value.replace(unicodeWordMatch, (txt => txt[0].toUpperCase() + txt.substring(1).toLowerCase()));
    }
}